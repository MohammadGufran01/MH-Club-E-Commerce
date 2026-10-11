import json
import time
import threading
from math import ceil
from decimal import Decimal
from datetime import timedelta

import razorpay
from razorpay.errors import SignatureVerificationError

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404 
from django.utils import timezone
from django.utils.http import urlencode

from django.views.decorators.csrf import csrf_exempt

from helper import send_email_async
from .models import Orders, OrderUpdate, Product, Contact, ProductVariant, Category
from .utils.refund import refund_payment

# Initialize Razorpay client helper safely using settings
def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def index(request):
    allProds = []
    categories = Category.objects.all()

    for cat in categories:
        products_qs = Product.objects.filter(category=cat).prefetch_related('additional_images')
        total_products = products_qs.count()

        if total_products > 4:
            products = products_qs.order_by('?')[:4]
        else:
            products = products_qs

        nSlides = ceil(len(products) / 4)
        if len(products) > 0:
            allProds.append([products, range(1, nSlides + 1), nSlides])

    return render(request, "index.html", {'allProds': allProds})


def contact(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, "Please login first to submit an inquiry.")
            return redirect('/auth/login/')
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        desc = request.POST.get('desc')
        phoneNo = request.POST.get('number')

        if not all([name, email, desc, phoneNo]):
            messages.error(request, "All fields are required.")
            return render(request, "contact.html")

        Contact.objects.create(name=name, email=email, desc=desc, phoneNo=phoneNo)
        messages.info(request, 'Thank you! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, "contact.html")


def about(request):
    return render(request, "about.html")


def sign(request):
    return redirect('auth:signup')


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login first")
        return redirect('/auth/login/')

    items_json = request.POST.get('itemsJson') or request.GET.get('itemsJson')
    items = json.loads(items_json) if items_json else {}
    product_ids = [int(str(pid).replace("pr","")) for pid in items.keys()]

    products = Product.objects.filter(id__in=product_ids).prefetch_related('additional_images')
    variants_map = {}
    params = {"itemsJson": items_json}

    for p in products:
        variants = ProductVariant.objects.filter(product=p, stock__gt=0)
        variants_map[p.id] = list(variants.values("id", "size__name", "stock"))

    user = request.user
    previous_orders = Orders.objects.filter(email=user.email)

    address1 = address2 = city = state = zip_code = phone = ''
    if previous_orders.exists():
        last = previous_orders.last()
        address1, address2, city, state, zip_code, phone = (
            last.address1, last.address2, last.city, last.state, last.zip_code, last.phone
        )

    if request.method == "POST":
        items_json = request.POST.get('itemsJson')
        cart = json.loads(items_json) if items_json else {}

        if not cart:
            messages.error(request, "Your cart is empty. Please add items before checkout.")
            return redirect(f"/checkout/?{urlencode(params)}")

        cart_items = []
        if isinstance(cart, dict):
            for pid, data in cart.items():
                if isinstance(data, list):
                    qty = int(data[0])
                    size = data[5] if len(data) > 5 else None
                else:
                    qty = int(data.get("qty", 1))
                    size = data.get("size")

                cart_items.append({
                    "pid": int(str(pid).replace("pr","")),
                    "qty": qty,
                    "size": size,
                })

        for item in cart_items:
            pid = item["pid"]
            qty = item["qty"]
            size = item["size"]
            variants = ProductVariant.objects.filter(product_id=pid)

            if variants.exists():
                if not size:
                    messages.error(request, "Please select size for all size-based products.")
                    return redirect(f"/checkout/?{urlencode(params)}")
                try:
                    variant = ProductVariant.objects.get(product_id=pid, size__name=size)
                except ProductVariant.DoesNotExist:
                    messages.error(request, "Selected size not available.")
                    return redirect(f"/checkout/?{urlencode(params)}")

                if variant.stock < qty:
                    messages.error(request, f"{variant.product.product_name} ({size}) is out of stock.")
                    return redirect(f"/checkout/?{urlencode(params)}")

        amount = Decimal(request.POST.get('amt') or "0")
        if amount <= 0:
            messages.error(request, "Invalid order amount.")
            return redirect(f"/checkout/?{urlencode(params)}")

        name = request.POST.get('name')
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        with transaction.atomic():
            order = Orders.objects.create(
                items_json=items_json, name=name, email=email, amount=amount,
                address1=address1, address2=address2, city=city, state=state,
                zip_code=zip_code, phone=phone
            )

            for item in cart_items:
                pid = item["pid"]
                qty = item["qty"]
                size = item["size"]
                variants = ProductVariant.objects.filter(product_id=pid)
                if variants.exists():
                    variant = ProductVariant.objects.get(product_id=pid, size__name=size)
                    variant.stock -= qty
                    variant.save()

            OrderUpdate.objects.create(order=order, update_desc="Order created. Waiting for payment.")

            if request.POST.get('payment_method') == "cod":
                order.oid = f"COD_{int(time.time())}" if 'time' in globals() else f"COD_{int(timezone.now().timestamp())}"
                order.paymentstatus = "Pending"
                OrderUpdate.objects.create(order=order, update_desc="Order placed successfully with Cash on Delivery.")
                order.save()
                return render(request, 'order_success.html', {'order': order})

            client = get_razorpay_client()
            razorpay_order = client.order.create({"amount": int(amount * 100), "currency": "INR"})
            order.oid = razorpay_order['id']
            order.paymentstatus = "Pending"
            order.amountpaid = amount
            OrderUpdate.objects.create(order=order, update_desc="Online payment initiated. Awaiting confirmation.")
            order.save()

            return render(request, "paytm.html", {
                "order_id": razorpay_order['id'],
                "key_id": settings.RAZORPAY_KEY_ID,
                "amount": int(amount * 100),
                "order": order
            })

    return render(request, 'checkout.html', {
        "OrderDetails": {
            "address1": address1, "address2": address2, "city": city,
            "state": state, "zip_code": zip_code, "phone": phone
        },
        "variants_map_json": json.dumps(variants_map)
    })


def order_activity(request, order_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login first")
        return redirect('/auth/login/')

    order = get_object_or_404(Orders, oid=order_id, email=request.user.email)
    items = json.loads(order.items_json or "{}") if isinstance(order.items_json, str) else (order.items_json or {})

    products = []
    for pid, value in items.items():
        try:
            clean_id = int(str(pid).replace("pr",""))
            product = Product.objects.prefetch_related('additional_images').get(id=clean_id)
            if isinstance(value, list):
                qty = value[0] if len(value) > 0 else 1
                price = value[2] if len(value) > 2 else product.price
                size = value[5] if len(value) > 5 else None
            else:
                qty = value.get("qty", 1)
                price = value.get("price", product.price)
                size = value.get("size")
            products.append({
                "product": product,
                "quantity": qty,
                "price": price,
                "size": size
            })
        except Exception:
            continue

    updates = order.updates.order_by('-update_date')
    return render(request, 'order_activity.html', {"order": order, "products": products, "updates": updates})


def payment_status(request):
    status = request.GET.get('status', 'unknown')
    razorpay_order_id = request.GET.get('razorpay_order_id', '')
    razorpay_payment_id = request.GET.get('razorpay_payment_id', '')
    message = request.GET.get('message', '')
    
    order = Orders.objects.filter(oid=razorpay_order_id).first()
    if not order:
        return render(request, 'paymentstatus.html', {
            'status': status,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'amount': 0,
            'message': 'Order information not found.'
        })

    if razorpay_payment_id:
        order.payment_id = razorpay_payment_id

    if status == 'success':
        order.paymentstatus = 'Paid'
        if not order.amountpaid:
            order.amountpaid = order.amount
        OrderUpdate.objects.get_or_create(order=order, update_desc="Payment received successfully via Razorpay.")
    elif status in ['failure', 'canceled']:
        if order.paymentstatus != 'Paid':
            order.paymentstatus = 'Cancelled'
            order.amountpaid = 0
            OrderUpdate.objects.get_or_create(order=order, update_desc="Payment cancelled by user during checkout.")
    else:
        if order.paymentstatus != 'Paid':
            order.paymentstatus = 'Pending'

    order.save()
    return render(request, 'paymentstatus.html', {
        'status': status,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'amount': order.amountpaid or order.amount,
        'message': message,
        'order': order
    })


@csrf_exempt
def handlerequest(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request"
        }, status=405)

    params_dict = {}

    try:
        data = json.loads(request.body)

        params_dict = {
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature"),
        }

        if not all(params_dict.values()):
            return JsonResponse({
                "status": "error",
                "message": "Missing payment data"
            }, status=400)

        # Verify Razorpay signature
        client = get_razorpay_client()
        client.utility.verify_payment_signature(params_dict)

        # Find our Django order
        order = Orders.objects.filter(
            oid=params_dict["razorpay_order_id"]
        ).first()

        if not order:
            return JsonResponse({
                "status": "error",
                "message": "Order not found"
            }, status=404)

        # Payment successfully verified
        order.paymentstatus = "Paid"
        order.amountpaid = order.amount
        order.payment_id = params_dict["razorpay_payment_id"]
        order.save()

        OrderUpdate.objects.create(
            order=order,
            update_desc="Payment successfully verified through Razorpay."
        )

        return JsonResponse({
            "status": "success"
        })

    except SignatureVerificationError:
        order = None

        if params_dict.get("razorpay_order_id"):
            order = Orders.objects.filter(
                oid=params_dict["razorpay_order_id"]
            ).first()

        if order:
            order.paymentstatus = "Failed"
            order.save()

            OrderUpdate.objects.create(
                order=order,
                update_desc="Razorpay payment signature verification failed."
            )

        return JsonResponse({
            "status": "error",
            "message": "Payment signature verification failed"
        }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON"
        }, status=400)

    except Exception as e:
        print("Razorpay verification error:", e)

        return JsonResponse({
            "status": "error",
            "message": "Payment verification failed"
        }, status=500)
def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login first")
        return redirect('/auth/login/')

    items = Orders.objects.filter(email=request.user.email).select_related("assigned_to").prefetch_related("updates").order_by("-BookDate")
    for order in items:
        try:
            order.products = json.loads(order.items_json or '{}')  
            latest = order.updates.order_by('-update_date').first()
            if order.assigned_to and latest and not latest.delivered:
                latest.update_desc = "Out for Delivery"
        except Exception:
            order.products = []

        if order.delivered_at:
            order.return_allowed = timezone.now() <= order.delivered_at + timedelta(days=5)
            order.return_allowed_date = order.delivered_at + timedelta(days=5)
        else:
            order.return_allowed = False

    updates = OrderUpdate.objects.filter(order__in=items).order_by('-update_date').first()
    return render(request, 'profile.html', {'items': items, 'updates': updates})


def productDetails(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related('additional_images', 'variants__size'),
        id=product_id
    )
    rating = min(product.Rating, 5) if product.Rating else 5
    stars = list(range(1, rating + 1))
    variants = product.variants.select_related('size').all()
    variants_data = [
        {"id": v.id, "size": v.size.name, "stock": v.stock}
        for v in variants
    ]
    return render(request, 'productDetail.html', {
        'product': product,
        'stars': stars,
        'variants': variants,
        'variants_json': json.dumps(variants_data)
    })


def category_products(request, category):
    import urllib.parse
    cleaned_category = urllib.parse.unquote_plus(category).strip()

    cat_obj = Category.objects.filter(name__iexact=cleaned_category).first()
    if not cat_obj and cleaned_category.isdigit():
        cat_obj = Category.objects.filter(id=int(cleaned_category)).first()

    if cat_obj:
        products = Product.objects.filter(category=cat_obj).prefetch_related('additional_images')
        display_name = cat_obj.name
    else:
        products = Product.objects.filter(
            Q(category__name__iexact=cleaned_category) |
            Q(subcategory__iexact=cleaned_category)
        ).prefetch_related('additional_images')
        display_name = cleaned_category

    return render(request, 'category_products.html', {'category': display_name, 'products': products})


def cancel_order(request, order_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login first")
        return redirect('/auth/login/')
    
    order = get_object_or_404(Orders, id=order_id, email=request.user.email)
    last_update = order.updates.last()
    if last_update and last_update.delivered:
        messages.error(request, "Delivered orders cannot be cancelled.")
        return redirect('profile')
    
    original_amount_paid = order.amountpaid
    order.paymentstatus = 'Cancelled'
    order.amountpaid = original_amount_paid if original_amount_paid > 0 else 0
    order.save()

    try:
        cart = json.loads(order.items_json or "{}")
        if isinstance(cart, dict):
            for pid, data in cart.items():
                product_id = int(str(pid).replace("pr",""))
                qty = int(data[0]) if isinstance(data, list) else int(data.get("qty", 1))
                size = data[5] if isinstance(data, list) and len(data) > 5 else data.get("size")
                if size:
                    variant = ProductVariant.objects.filter(product_id=product_id, size__name=size).first()
                    if variant:
                        variant.stock += qty
                        variant.save()
    except Exception as e:
        print("STOCK RESTORE ERROR:", e)
        
    if last_update:
        last_update.update_desc = "The order has been cancelled by the user."
        last_update.delivered = False
        last_update.save()
    else:
        order.updates.create(update_desc="The order has been cancelled by the user.", delivered=False)

    messages.success(request, f"Order #{order.oid} cancelled successfully")
    return redirect('profile')


def return_order(request, order_id):
    order = get_object_or_404(Orders, id=order_id, email=request.user.email)
    if not order.delivered_at:
        messages.error(request, "This order has not been delivered yet.")
        return redirect('profile')
    if order.is_returned:
        messages.warning(request, "This order is already returned.")
        return redirect('profile')

    return_last_date = order.delivered_at + timedelta(days=5)
    if timezone.now() > return_last_date:
        messages.error(request, "Return period has expired (5 days).")
        return redirect('profile')

    order.is_returned = True
    OrderUpdate.objects.create(order=order, update_desc="Return requested — assigned for pickup", delivered=False)
    order.save()
    messages.success(request, "Return request submitted. Our delivery partner will pick it up soon.")
    return redirect('profile')


def search(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) | Q(desc__icontains=query) | Q(category__name__icontains=query)
        ).prefetch_related('additional_images')
    
    return render(request, 'category_products.html', {
        'products': products,
        'query': query,
        'is_search': True
    })


def live_search_api(request):
    query = request.GET.get('q', '').strip()
    products = []
    if query:
        product_qs = Product.objects.filter(product_name__icontains=query).prefetch_related('additional_images')[:5]
        for p in product_qs:
            first_img = p.additional_images.first()
            products.append({
                'id': p.id,
                'name': p.product_name,
                'price': p.price,
                'image': first_img.image.url if first_img else '',
                'url': f'/productDetails/{p.id}/'
            })
    return JsonResponse({'products': products})


def custom_400_view(request, exception=None):
    return render(request, '400.html', status=400)


def custom_403_view(request, exception=None):
    return render(request, '403.html', status=403)


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)