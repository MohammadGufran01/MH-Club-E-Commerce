import json
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, ProductVariant, Category, Orders, CancelledPaidOrder, Contact
from delivery.models import DeliveryBoy, DeliveryOTP


def dashboard_callback(request, context):
    """
    Computes rich statistical analytics, time-series data, KPI metrics,
    inventory alerts, full products catalog, and live activity feeds for the animated Admin Dashboard.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ==================== 1. FINANCIAL & REVENUE METRICS ====================
    revenue_agg = Orders.objects.filter(
        Q(paymentstatus="Paid") | Q(paymentstatus="Delivered") | Q(amountpaid__gt=0)
    ).aggregate(
        total_rev=Sum("amountpaid"),
        total_value=Sum("amount")
    )
    total_revenue = float(revenue_agg["total_rev"] or revenue_agg["total_value"] or 0)

    today_revenue_agg = Orders.objects.filter(
        BookDate__gte=today_start
    ).filter(
        Q(paymentstatus="Paid") | Q(paymentstatus="Delivered") | Q(amountpaid__gt=0)
    ).aggregate(total=Sum("amountpaid"))
    today_revenue = float(today_revenue_agg["total"] or 0)

    month_revenue_agg = Orders.objects.filter(
        BookDate__gte=month_start
    ).filter(
        Q(paymentstatus="Paid") | Q(paymentstatus="Delivered") | Q(amountpaid__gt=0)
    ).aggregate(total=Sum("amountpaid"))
    month_revenue = float(month_revenue_agg["total"] or 0)

    paid_orders_count = Orders.objects.filter(
        Q(paymentstatus="Paid") | Q(paymentstatus="Delivered") | Q(amountpaid__gt=0)
    ).count()
    avg_order_value = round(total_revenue / paid_orders_count, 2) if paid_orders_count > 0 else 0

    refunded_agg = CancelledPaidOrder.objects.filter(is_refunded=True).aggregate(total=Sum("amountpaid"))
    total_refunded = float(refunded_agg["total"] or 0)
    pending_refunds_count = CancelledPaidOrder.objects.filter(is_refunded=False, amountpaid__gt=0).count()

    # ==================== 2. ORDER PIPELINE & FULFILLMENT ====================
    total_orders = Orders.objects.count()
    orders_paid = Orders.objects.filter(paymentstatus="Paid").count()
    orders_pending = Orders.objects.filter(paymentstatus__in=["Pending", "Placed"]).count()
    orders_cancelled = Orders.objects.filter(paymentstatus="Cancelled").count()
    orders_returned = Orders.objects.filter(paymentstatus__in=["Return Completed", "Returned"]).count()
    orders_delivered = Orders.objects.filter(paymentstatus="Delivered").count()

    successful_orders = orders_paid + orders_delivered
    fulfillment_rate = round((successful_orders / total_orders * 100), 1) if total_orders > 0 else 0
    today_orders_count = Orders.objects.filter(BookDate__gte=today_start).count()

    # ==================== 3. INVENTORY & CATALOG HEALTH ====================
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_variants = ProductVariant.objects.count()

    # Low Stock Alerts (Stock <= 5) and Out of Stock (Stock == 0)
    low_stock_variants = []
    out_of_stock_count = 0
    low_stock_count = 0

    for variant in ProductVariant.objects.select_related("product", "size").order_by("stock")[:15]:
        if variant.stock == 0:
            out_of_stock_count += 1
            low_stock_variants.append({
                "product_name": variant.product.product_name,
                "product_id": variant.product.id,
                "size": variant.size.name,
                "stock": variant.stock,
                "status": "Out of Stock",
                "badge_class": "bg-red-500/20 text-red-400 border-red-500/30",
                "edit_url": reverse("admin:buyzoneapp_product_change", args=[variant.product.id])
            })
        elif variant.stock <= 5:
            low_stock_count += 1
            low_stock_variants.append({
                "product_name": variant.product.product_name,
                "product_id": variant.product.id,
                "size": variant.size.name,
                "stock": variant.stock,
                "status": "Low Stock",
                "badge_class": "bg-amber-500/20 text-amber-400 border-amber-500/30",
                "edit_url": reverse("admin:buyzoneapp_product_change", args=[variant.product.id])
            })

    # ==================== 4. COMPLETE PRODUCTS CATALOG LIST FOR DASHBOARD ====================
    catalog_products_list = []
    for prod in Product.objects.select_related("category").prefetch_related("variants__size", "additional_images").order_by("-id"):
        first_img = prod.additional_images.first()
        img_url = first_img.image.url if first_img and hasattr(first_img.image, "url") else None

        prod_variants = []
        tot_stock = 0
        for v in prod.variants.all():
            tot_stock += v.stock
            prod_variants.append({
                "size": v.size.name,
                "stock": v.stock,
                "is_low": v.stock <= 5,
                "is_out": v.stock == 0
            })

        catalog_products_list.append({
            "id": prod.id,
            "product_name": prod.product_name,
            "category": prod.category.name if prod.category else "Uncategorized",
            "subcategory": prod.subcategory or "",
            "price": prod.price,
            "old_price": prod.OldPrice,
            "discount": prod.Discount,
            "rating": prod.Rating,
            "rating_stars": "⭐" * prod.Rating if prod.Rating else "—",
            "image_url": img_url,
            "variants": prod_variants,
            "total_stock": tot_stock,
            "edit_url": reverse("admin:buyzoneapp_product_change", args=[prod.id]),
        })

    # ==================== 5. USERS & LOGISTICS METRICS ====================
    total_customers = User.objects.filter(is_staff=False).count()
    total_delivery_boys = DeliveryBoy.objects.count()
    active_assignments = Orders.objects.filter(assigned_to__isnull=False, delivered_at__isnull=True).count()
    verified_otps = DeliveryOTP.objects.filter(verified=True).count()
    pending_otps = DeliveryOTP.objects.filter(verified=False).count()

    # ==================== 6. TIME-SERIES DATA FOR APEXCHARTS ====================
    timeline_days_7 = []
    revenue_series_7 = []
    orders_series_7 = []

    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_label = day_date.strftime("%b %d")
        timeline_days_7.append(day_label)

        day_orders = Orders.objects.filter(BookDate__date=day_date)
        orders_cnt = day_orders.count()
        orders_series_7.append(orders_cnt)

        day_rev = day_orders.filter(
            Q(paymentstatus="Paid") | Q(paymentstatus="Delivered") | Q(amountpaid__gt=0)
        ).aggregate(tot=Sum("amountpaid"))["tot"] or 0
        revenue_series_7.append(float(day_rev))

    if sum(revenue_series_7) == 0 and total_revenue > 0:
        revenue_series_7[-1] = total_revenue

    if sum(orders_series_7) == 0 and total_orders > 0:
        orders_series_7[-1] = total_orders

    timeline_days_30 = []
    revenue_series_30 = []
    orders_series_30 = []
    for i in range(29, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        timeline_days_30.append(day_date.strftime("%d %b"))
        day_orders = Orders.objects.filter(BookDate__date=day_date)
        orders_series_30.append(day_orders.count())
        day_rev = day_orders.filter(
            Q(paymentstatus="Paid") | Q(paymentstatus="Delivered") | Q(amountpaid__gt=0)
        ).aggregate(tot=Sum("amountpaid"))["tot"] or 0
        revenue_series_30.append(float(day_rev))

    categories_data = []
    categories_labels = []
    categories_counts = []
    for cat in Category.objects.annotate(prod_count=Count("product")).order_by("-prod_count")[:6]:
        categories_labels.append(cat.name)
        categories_counts.append(cat.prod_count)
        categories_data.append({
            "name": cat.name,
            "count": cat.prod_count,
        })

    order_status_labels = ["Paid / Delivered", "Pending / Processing", "Cancelled", "Return Completed"]
    order_status_series = [
        orders_paid + orders_delivered,
        orders_pending,
        orders_cancelled,
        orders_returned
    ]

    online_orders = Orders.objects.filter(payment_id__isnull=False).exclude(payment_id="").count()
    cod_orders = max(0, total_orders - online_orders)

    # ==================== 7. RECENT ACTIVITY & FEEDS ====================
    recent_orders_list = []
    for order in Orders.objects.order_by("-BookDate")[:8]:
        status_color = "slate"
        pulse = False
        if order.paymentstatus in ["Paid", "Delivered"]:
            status_color = "emerald"
        elif order.paymentstatus in ["Pending", "Placed"]:
            status_color = "amber"
            pulse = True
        elif order.paymentstatus in ["Cancelled"]:
            status_color = "rose"
        elif order.paymentstatus in ["Return Completed", "Returned"]:
            status_color = "purple"

        item_count = 0
        try:
            if order.items_json:
                data = json.loads(order.items_json) if isinstance(order.items_json, str) else order.items_json
                item_count = len(data)
        except Exception:
            item_count = 1

        recent_orders_list.append({
            "id": order.id,
            "oid": order.oid or f"ORD-{order.id}",
            "name": order.name,
            "email": order.email,
            "amount": float(order.amount),
            "amountpaid": float(order.amountpaid),
            "paymentstatus": order.paymentstatus,
            "status_color": status_color,
            "pulse": pulse,
            "item_count": item_count,
            "date": order.BookDate.strftime("%b %d, %I:%M %p") if order.BookDate else "-",
            "view_url": reverse("admin:buyzoneapp_orders_change", args=[order.id])
        })

    recent_contacts = []
    for contact in Contact.objects.order_by("-id")[:5]:
        recent_contacts.append({
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phoneNo,
            "desc": (contact.desc[:70] + "...") if len(contact.desc) > 70 else contact.desc,
            "view_url": reverse("admin:buyzoneapp_contact_change", args=[contact.id])
        })

    # ==================== 8. INJECT INTO CONTEXT ====================
    context.update({
        # KPI Stats
        "kpi_total_revenue": total_revenue,
        "kpi_today_revenue": today_revenue,
        "kpi_month_revenue": month_revenue,
        "kpi_avg_order_value": avg_order_value,
        "kpi_total_refunded": total_refunded,
        "kpi_pending_refunds": pending_refunds_count,
        "kpi_total_orders": total_orders,
        "kpi_today_orders": today_orders_count,
        "kpi_orders_paid": orders_paid,
        "kpi_orders_pending": orders_pending,
        "kpi_orders_cancelled": orders_cancelled,
        "kpi_orders_returned": orders_returned,
        "kpi_orders_delivered": orders_delivered,
        "kpi_fulfillment_rate": fulfillment_rate,
        "kpi_total_products": total_products,
        "kpi_total_categories": total_categories,
        "kpi_total_variants": total_variants,
        "kpi_low_stock_count": low_stock_count + out_of_stock_count,
        "kpi_out_of_stock_count": out_of_stock_count,
        "kpi_total_customers": total_customers,
        "kpi_total_delivery_boys": total_delivery_boys,
        "kpi_active_assignments": active_assignments,
        "kpi_verified_otps": verified_otps,
        "kpi_pending_otps": pending_otps,

        # Chart JSON Series
        "chart_timeline_7_labels": json.dumps(timeline_days_7),
        "chart_timeline_7_revenue": json.dumps(revenue_series_7),
        "chart_timeline_7_orders": json.dumps(orders_series_7),
        "chart_timeline_30_labels": json.dumps(timeline_days_30),
        "chart_timeline_30_revenue": json.dumps(revenue_series_30),
        "chart_timeline_30_orders": json.dumps(orders_series_30),
        "chart_order_status_labels": json.dumps(order_status_labels),
        "chart_order_status_series": json.dumps(order_status_series),
        "chart_categories_labels": json.dumps(categories_labels),
        "chart_categories_series": json.dumps(categories_counts),
        "chart_payment_series": json.dumps([online_orders, cod_orders]),
        "chart_payment_labels": json.dumps(["Online (Razorpay)", "Cash on Delivery"]),

        # Data Lists
        "catalog_products": catalog_products_list,
        "recent_orders": recent_orders_list,
        "low_stock_variants": low_stock_variants,
        "recent_contacts": recent_contacts,
        "categories_summary": categories_data,
        "current_time_display": now.strftime("%A, %B %d, %Y"),
    })

    return context
