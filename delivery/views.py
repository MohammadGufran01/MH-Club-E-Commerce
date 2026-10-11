import json
import random
import threading
from django.shortcuts import render, redirect, get_object_or_404
from buyzoneapp.models import Orders, OrderUpdate
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import localdate
from django.db.models import Sum

from helper import send_email_async
from .models import DeliveryOTP
from buyzoneapp.models import Orders, OrderUpdate, Product
from django.db.models import OuterRef, Exists, Q
from .utils.receipt import build_modern_invoice
from django.core.mail import send_mail



def delivery_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.groups.filter(name='DeliveryBoy').exists()
    )(view_func)


@login_required
@delivery_required
def generate_delivery_otp(request, order_id):
    order = get_object_or_404(Orders, id=order_id)

    otp = str(random.randint(100000, 999999))

    DeliveryOTP.objects.update_or_create(
        order=order,
        defaults={
            "otp": otp,
            "verified": False,
            "created_at": timezone.now()   # RESET expiry time
        }
    )


    subject = "Your MH Club Delivery OTP"

    html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <title>MH Club Delivery OTP</title>
        </head>

        <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, Helvetica, sans-serif;">

        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f8; padding:20px 0;">
        <tr>
        <td align="center">

        <!-- Main Container -->
        <table width="600" cellpadding="0" cellspacing="0" 
        style="background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1);">

        <!-- Header -->
        <tr>
        <td style="background-color:#111111; padding:25px; text-align:center;">
        <h1 style="color:#ffffff; margin:0; font-size:26px; letter-spacing:1px;">MH Club</h1>
        <p style="color:#e9ecef; margin:5px 0 0; font-size:14px;">
            Secure Delivery Verification
        </p>
        </td>
        </tr>

        <!-- Body -->
        <tr>
        <td style="padding:30px; color:#333333;">

        <h2 style="margin-top:0;">Hi {order.name}, 👋</h2>

        <p style="font-size:15px; line-height:1.6;">
            Your delivery is on the way! To securely confirm your order delivery,
            please share the OTP below with your delivery partner.
        </p>

        <!-- OTP BOX -->
        <div style="text-align:center; margin:30px 0;">
            <div style="
            display:inline-block;
            background:#111111;
            color:#ffffff;
            padding:14px 30px;
            font-size:26px;
            border-radius:10px;
            letter-spacing:6px;
            font-weight:bold;
            ">
            {otp}
            </div>

            <p style="font-size:13px; color:#6c757d; margin-top:10px;">
            This OTP is valid for 5 minutes. Do not share it with anyone else.
            </p>
        </div> <br>
        <p style="font-size:14px; line-height:1;">
            Total amount to be paid: <strong>₹ {order.amount}</strong>
        </p>
        <p style="font-size:14px; line-height:1;">
            Delivery for Order ID: <strong>{order.oid}</strong>
        </p>

        <p style="font-size:14px; line-height:1.6;">
            If you did not expect this delivery, please contact our support team immediately.
        </p>

        <p style="margin-top:30px; font-size:14px;">
            Regards,<br>
            <strong>MH Club Team</strong>
        </p>

        </td>
        </tr>

        <!-- Footer -->
        <tr>
        <td style="background-color:#f8f9fa; padding:15px; text-align:center; font-size:12px; color:#6c757d;">
        © 2026 MH Club. All rights reserved.
        </td>
        </tr>

        </table>

        </td>
        </tr>
        </table>

        </body>
        </html>
        """

        # Plain-text fallback (required for some clients)
    text_message = f"Your MH Club Delivery OTP is {otp}. Do not share it with anyone."

    email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email]
    )
    
    email.attach_alternative(html_message, "text/html")
    threading.Thread(target=send_email_async, args=(email,)).start()

    messages.success(request, "OTP sent to customer email")
    return redirect("verify_delivery_otp", order_id=order.id)


@login_required
@delivery_required
def verify_delivery_otp(request, order_id):
    order = get_object_or_404(Orders, id=order_id)
    delivery_otp = get_object_or_404(DeliveryOTP, order=order)
    

    if request.method == "POST":
        entered = request.POST.get("otp")

        if delivery_otp.is_expired():
            messages.error(request, "OTP expired. Generate a new one.")
            return redirect("generate_delivery_otp", order.id)

        if delivery_otp.otp == entered:

            delivery_otp.verified = True
            delivery_otp.save()

            otp = delivery_otp.otp
            subject = "Confirmation: Your MH Club Order is Delivered"

            html_message = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="UTF-8">
                <title>MH Club — Order Delivered</title>
                </head>

                <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, Helvetica, sans-serif;">

                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f8; padding:20px 0;">
                <tr>
                <td align="center">

                <!-- Main Container -->
                <table width="600" cellpadding="0" cellspacing="0" 
                style="background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1);">

                <!-- Header -->
                <tr>
                <td style="background-color:#111111; padding:25px; text-align:center;">
                <h1 style="color:#ffffff; margin:0; font-size:26px; letter-spacing:1px;">MH Club</h1>
                <p style="color:#e9ecef; margin:5px 0 0; font-size:14px;">
                    Order Delivery Confirmation
                </p>
                </td>
                </tr>

                <!-- Body -->
                <tr>
                <td style="padding:30px; color:#333333;">

                <h2 style="margin-top:0;">Hi {order.name}, 🎉</h2>

                <p style="font-size:15px; line-height:1.6;">
                    We’re happy to let you know that your order has been successfully delivered.
                </p>

                <p style="font-size:15px; line-height:1.6;">
                    Thank you for shopping with <strong>MH Club</strong>. We hope you enjoy your purchase!
                </p>

                <!-- Order Info box -->
                <div style="margin:25px 0; text-align:center;">
                    <table cellpadding="0" cellspacing="0" style="border:1px solid #e4e6eb; border-radius:10px; padding:15px; display:inline-block;">
                    <tr>
                        <td style="font-size:14px; color:#333;">
                        <strong>Order ID:</strong> {order.oid}
                        </td>
                    </tr>
                    <tr>
                        <td style="font-size:14px; color:#333;">
                        <strong>Status:</strong> Delivered ✔
                        </td>
                    </tr>
                    </table>
                </div>

                <p style="font-size:14px; line-height:1.6;">
                    If you did not receive this order or have any concerns, please contact our support team immediately.
                </p>

                <p style="margin-top:30px; font-size:14px;">
                    Warm Regards,<br>
                    <strong>MH Club Team</strong>
                </p>

                </td>
                </tr>

                <!-- Footer -->
                <tr>
                <td style="background-color:#f8f9fa; padding:15px; text-align:center; font-size:12px; color:#6c757d;">
                © 2026 MH Club. All rights reserved.
                </td>
                </tr>

                </table>

                </td>
                </tr>
                </table>

                </body>
                </html>
            """


            text_message = f"Order Delivered: Your MH Club order with ID {order.oid} has been delivered successfully."

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.email]
            )

            order.paymentstatus = "Paid"
            order.amountpaid = order.amountpaid or order.amount
            order.delivered_at = timezone.now()
            order.save(update_fields=["paymentstatus","amountpaid","delivered_at"])

            email.attach_alternative(html_message, "text/html")

            pdf_buffer = build_modern_invoice(order)
            email.attach(
                filename=f"MH_Club_Invoice_{order.oid}.pdf",
                content=pdf_buffer.getvalue(),
                mimetype="application/pdf"
            )

            threading.Thread(target=send_email_async, args=(email,)).start()


            

            OrderUpdate.objects.create(
                order=order,
                update_desc="The order has been delivered successfully.",
                delivered=True
            )


            messages.success(request, "Delivery confirmed successfully")
            return redirect("delivery_dashboard")

        messages.error(request, "Incorrect OTP")

    return render(request, "delivery/verify.html", {"order": order})


@login_required
@delivery_required
def delivery_dashboard(request):

    delivered_updates = OrderUpdate.objects.filter(
        order=OuterRef('pk'), delivered=True
    )

    orders = Orders.objects.annotate(
        is_delivered=Exists(delivered_updates)
    ).filter(
        assigned_to=request.user,
        paymentstatus__in=["Pending", "Paid"],
        is_delivered=False,
        is_returned=False
    ).order_by('-id')

    for o in orders:
        try:
            o.items = json.loads(o.items_json or "{}")
        except:
            o.items = {}

    activity = (
        OrderUpdate.objects
        .filter(order__assigned_to=request.user)
        .filter(update_desc__icontains="Assigned")
        .select_related("order")
        .order_by('-update_date')
    )

    return render(request, "delivery/dashboard.html", {
        "orders": orders,
        "activity": activity
    })


@login_required
@delivery_required
def delivery_stats(request):
    user = request.user
    today = localdate()

    # Total assigned to this delivery boy
    total_assigned = Orders.objects.filter(
        assigned_to=user
    ).count()

    # Delivered (OTP verified)
    delivered_count = Orders.objects.filter(
        assigned_to=user,
        deliveryotp__verified=True
    ).count()

    # Pending (assigned but NOT delivered yet)
    pending_count = Orders.objects.filter(
        assigned_to=user
    ).exclude(
        paymentstatus="Cancelled"
    ).filter(
        Q(deliveryotp__verified=False) | Q(deliveryotp__isnull=True)
    ).distinct().count()

    # Delivered today
    today_delivered = Orders.objects.filter(
        assigned_to=user,
        deliveryotp__verified=True,
        deliveryotp__created_at__date=today
    ).count()

    # Cancelled orders (based on your field)
    cancelled_count = Orders.objects.filter(
        assigned_to=user,
        paymentstatus="Cancelled"
    ).count()

    # Total cash collected (based on amountpaid)
    cash_collected = Orders.objects.filter(
        assigned_to=user,
        deliveryotp__verified=True
    ).aggregate(total=Sum("amountpaid"))["total"] or 0

    # Last 10 assigned orders
    recent_orders = Orders.objects.filter(
        assigned_to=user,
        paymentstatus__in=["Pending", "Paid", "Cancelled"]
    ).order_by("-id")[:10]

    context = {
        "total_assigned": total_assigned,
        "delivered_count": delivered_count,
        "pending_count": pending_count,
        "today_delivered": today_delivered,
        "cancelled_count": cancelled_count,
        "cash_collected": cash_collected,
        "recent_orders": recent_orders,
    }

    return render(request, "delivery/stats.html", context)


@login_required
@delivery_required
def orderDetails(request, order_id):
    order = get_object_or_404(Orders, oid=order_id)

    updates = OrderUpdate.objects.filter(order=order).order_by('-update_date')

    items_raw = json.loads(order.items_json or "{}") if isinstance(order.items_json, str) else (order.items_json or {})
    product_ids = []
    for pid in items_raw.keys():
        try:
            clean_id = int(str(pid).replace("pr", ""))
            product_ids.append(clean_id)
        except (ValueError, TypeError):
            continue

    products = {p.id: p for p in Product.objects.filter(id__in=product_ids).prefetch_related('additional_images')}

    items_list = []
    for pid, v in items_raw.items():
        try:
            clean_id = int(str(pid).replace("pr", ""))
            p = products.get(clean_id)
            img_url = p.main_image if p else ""
            if isinstance(v, list):
                qty = v[0] if len(v) > 0 else 1
                name = v[1] if len(v) > 1 else (p.product_name if p else "Product")
                price = v[2] if len(v) > 2 else (p.price if p else 0)
                mrp = v[3] if len(v) > 3 else (p.OldPrice if p else 0)
                discount = v[4] if len(v) > 4 else (p.Discount if p else 0)
                size = v[5] if len(v) > 5 else ""
            else:
                qty = v.get("qty", 1)
                name = v.get("name", p.product_name if p else "Product")
                price = v.get("price", p.price if p else 0)
                mrp = v.get("mrp", p.OldPrice if p else 0)
                discount = v.get("discount", p.Discount if p else 0)
                size = v.get("size", "")

            items_list.append({
                "pid": pid,
                "name": name,
                "qty": qty,
                "price": price,
                "mrp": mrp,
                "discount": discount,
                "size": size,
                "image": img_url,
            })
        except Exception:
            continue

    context = {
        "order": order,
        "updates": updates,
        "items": items_raw,
        "items_list": items_list,
    }

    return render(request, "delivery/orderDetails.html", context)


@login_required
@delivery_required
def mark_return_picked(request, order_id):

    order = get_object_or_404(
        Orders,
        id=order_id,
        assigned_to=request.user
    )

    if not order.is_returned:
        messages.error(request, "This order is not marked for return.")
        return redirect("delivery_dashboard")

    order.delivered_at = timezone.now()
    order.assigned_to = None

    if order.payment_id:
        order.paymentstatus = "Cancelled"
        order.is_refunded = False
        order.save()

        OrderUpdate.objects.create(
            order=order,
            update_desc="Return picked. Refund will be processed after verification",
            delivered=False
        )

        send_mail(
            subject="Return picked – refund in progress",
            message=(
                f"Hi {order.name},\n\n"
                f"We’ve picked up your return for Order ID {order.oid}.\n\n"
                "Our team will verify the item and process your refund shortly.\n"
                "Refunds are usually completed within 5–7 business days.\n\n"
                "— MH Club Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True,
        )

    else:
        order.paymentstatus = "Return Completed"
        order.is_refunded = False
        order.save()

        OrderUpdate.objects.create(
            order=order,
            update_desc="Return picked successfully (COD order)",
            delivered=False
        )

        send_mail(
            subject="Return picked successfully",
            message=(
                f"Hi {order.name},\n\n"
                f"We’ve successfully picked up your return for Order ID {order.oid}.\n\n"
                "Since this was a Cash on Delivery order, the refund process is handled by our team within 5–7 business days.\n\n"
                "— MH Club Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True,
        )

    messages.success(request, "Return pickup completed successfully.")
    return redirect("return_dashboard")

@login_required
@delivery_required
def return_order_picked(request):
    user = request.user

    returns = Orders.objects.filter(
        assigned_to=user,
        is_returned=True
    ).order_by("-id")

    for o in returns:
        try:
            o.items = json.loads(o.items_json or "{}")
            print(json.loads(o.items_json or "{}"))
        except:
            o.items = {}

    activity = (
        OrderUpdate.objects
        .filter(order__assigned_to=user)
        .filter(update_desc__icontains="Return")
        .select_related("order")
        .order_by("-update_date")[:20]
    )
    return render(request, "delivery/return.html", {
        "returns": returns,
        "activity": activity
    })
