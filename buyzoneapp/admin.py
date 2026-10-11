import json
from django.contrib import admin, messages
from django.utils.html import escape
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from .models import (
    Product,
    ProductImage,
    ProductVariant,
    Size,
    Orders,
    OrderUpdate,
    Contact,
    CancelledPaidOrder,
    Category,
    Subcategory
)
from .utils.refund import refund_payment


# ==================== CATEGORY & SUBCATEGORY ADMIN ====================

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('id', 'name_badge', 'products_count')
    search_fields = ('name',)

    def name_badge(self, obj):
        name = escape(obj.name or "Unnamed")
        return mark_safe(
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<span class="material-symbols-outlined" style="color:#6366f1;font-size:20px;">category</span>'
            f'<strong style="font-size:14px;">{name}</strong>'
            f'</div>'
        )
    name_badge.short_description = "Category Name"

    def products_count(self, obj):
        cnt = obj.product_set.count()
        return mark_safe(f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300">{cnt} Products</span>')
    products_count.short_description = "Catalog Items"


@admin.register(Subcategory)
class SubcategoryAdmin(ModelAdmin):
    list_display = ('id', 'name', 'category_badge')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

    def category_badge(self, obj):
        cat_name = escape(obj.category.name if obj.category else "None")
        return mark_safe(f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200">📂 {cat_name}</span>')
    category_badge.short_description = "Parent Category"


# ==================== CATEGORY FILTER FOR PRODUCTS ====================

class CategoryFilter(admin.SimpleListFilter):
    title = 'Category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Category.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
        return queryset


# ==================== ADMIN IMAGE & VARIANTS INLINES ====================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        'id',
        'product_image',
        'product_name_display',
        'category_display',
        'price_display',
        'discount_display',
        'inventory_summary',
        'rating_stars'
    )

    fieldsets = (
        ('Basic Information', {'fields': ('product_name', 'category', 'subcategory')}),
        ('Pricing & Charges', {'fields': ('price', 'OldPrice', 'Discount', 'ShippingFee')}),
        ('Customer Rating', {'fields': ('Rating',)}),
        ('Product Description', {'fields': ('desc',)}),
    )

    readonly_fields = ('Discount',)
    inlines = [ProductImageInline, ProductVariantInline]
    search_fields = ('product_name', 'category__name', 'subcategory', 'id')
    list_display_links = ('id', 'product_name_display')
    list_filter = (CategoryFilter, 'Rating')

    def product_name_display(self, obj):
        pname = escape(obj.product_name or "")
        return mark_safe(f'<strong style="font-size:13px;color:var(--color-primary-600, #4f46e5);">{pname}</strong>')
    product_name_display.short_description = "Product Name"

    def category_display(self, obj):
        cat_name = escape(obj.category.name if obj.category else "Uncategorized")
        sub_name = f" · {escape(obj.subcategory)}" if obj.subcategory else ""
        return mark_safe(f'<span style="font-size:12px;opacity:0.85;">{cat_name}{sub_name}</span>')
    category_display.short_description = "Category"

    def price_display(self, obj):
        price = obj.price or 0
        old_price = obj.OldPrice or 0
        if old_price > price:
            return mark_safe(f'<strong style="color:#10b981;font-size:13px;">₹{price}</strong> <del style="color:#ef4444;font-size:11px;opacity:0.75;">₹{old_price}</del>')
        return mark_safe(f'<strong style="color:#10b981;font-size:13px;">₹{price}</strong>')
    price_display.short_description = "Price (₹)"

    def discount_display(self, obj):
        disc = obj.Discount or 0
        if disc > 0:
            return mark_safe(f'<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400">{disc}% OFF</span>')
        return "—"
    discount_display.short_description = "Discount"

    def inventory_summary(self, obj):
        variants = obj.variants.all()
        if not variants.exists():
            return mark_safe('<span style="color:#ef4444;font-size:11px;">No variants</span>')
        
        pills = []
        for v in variants:
            size_name = escape(v.size.name if v.size else "")
            color = "#10b981" if v.stock > 5 else ("#f59e0b" if v.stock > 0 else "#ef4444")
            pills.append(f'<span style="display:inline-block;padding:1px 6px;margin:2px;border-radius:4px;background:rgba(0,0,0,0.05);font-size:11px;"><strong style="color:{color};">{size_name}:</strong> {v.stock}</span>')
        return mark_safe("".join(pills))
    inventory_summary.short_description = "Variant Stocks"

    def rating_stars(self, obj):
        return "⭐" * obj.Rating if obj.Rating else "—"
    rating_stars.short_description = "Rating"

    @admin.display(description="Thumbnail")
    def product_image(self, obj):
        first_img = obj.additional_images.first()
        if first_img and first_img.image and hasattr(first_img.image, 'url'):
            return mark_safe(f'<img src="{first_img.image.url}" loading="lazy" width="44" height="44" style="border-radius:10px; object-fit:cover; box-shadow:0 2px 8px rgba(0,0,0,0.1);"/>')
        return "—"


# ==================== SIZE ADMIN ====================

@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ("id", "name_badge")
    search_fields = ("name",)

    def name_badge(self, obj):
        sname = escape(obj.name or "")
        return mark_safe(f'<span style="font-weight:700;font-size:13px;padding:3px 10px;border-radius:6px;background:rgba(99,102,241,0.1);color:#6366f1;">{sname}</span>')
    name_badge.short_description = "Size"


# ==================== PRODUCT VARIANT ADMIN ====================

@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    list_display = ("product_info", "size_badge", "stock_badge")
    search_fields = ("product__product_name", "product__id", "size__name")
    list_filter = ("size",)

    def product_info(self, obj):
        pname = escape(obj.product.product_name if obj.product else "N/A")
        pid = obj.product.id if obj.product else "?"
        return mark_safe(f'<strong>#{pid} · {pname}</strong>')
    product_info.short_description = "Product"

    def size_badge(self, obj):
        sname = escape(obj.size.name if obj.size else "N/A")
        return mark_safe(f'<span style="font-weight:600;padding:2px 8px;border-radius:6px;background:rgba(0,0,0,0.06);">{sname}</span>')
    size_badge.short_description = "Size"

    def stock_badge(self, obj):
        stock = obj.stock or 0
        if stock == 0:
            return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300 animate-pulse">Out of Stock (0)</span>')
        elif stock <= 5:
            return mark_safe(f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">⚠️ Low Stock ({stock})</span>')
        return mark_safe(f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">✓ In Stock ({stock})</span>')
    stock_badge.short_description = "Stock Status"


# ==================== ORDER UPDATE ADMIN ====================

@admin.register(OrderUpdate)
class OrderUpdateAdmin(ModelAdmin):
    list_display = ('order_oid', 'short_update', 'delivered_badge', 'update_date')
    list_editable = ()
    list_filter = ('delivered', 'update_date')
    readonly_fields = ('update_date',)
    ordering = ('-update_date',)
    search_fields = ('order__oid',)

    def has_add_permission(self, request):
        return False

    def short_update(self, obj):
        desc = obj.update_desc or ""
        return desc[:65] + "..." if len(desc) > 65 else desc

    def order_oid(self, obj):
        oid = escape(obj.order.oid if obj.order and obj.order.oid else f"ORD-{obj.order.id if obj.order else 'N/A'}")
        oid_num = obj.order.id if obj.order else 'N/A'
        return mark_safe(f'<strong>Order #{oid_num}</strong> ({oid})')
    order_oid.short_description = "Order"

    def delivered_badge(self, obj):
        if obj.delivered:
            return mark_safe('<span style="color:#10b981;font-weight:700;">✓ Delivered</span>')
        return mark_safe('<span style="color:#f59e0b;font-weight:700;">⏳ In Progress</span>')
    delivered_badge.short_description = "Fulfillment"


# ==================== ORDERS ADMIN ====================

@admin.register(Orders)
class OrdersAdmin(ModelAdmin):
    list_display = (
        'order_oid_display',
        'customer_display',
        'amount_display',
        'payment_status_badge',
        'delivery_agent_display',
        'BookDate',
    )
    list_display_links = ('order_oid_display',)
    list_filter = ('paymentstatus', 'BookDate', 'is_returned', 'is_refunded')
    search_fields = ('oid', 'email', 'name', 'phone')
    date_hierarchy = 'BookDate'
    exclude = ('items_json',)

    readonly_fields = (
        'items_json_formatted',
        'amount',
        'amountpaid',
        'BookDate',
        'is_returned',
        'delivered_at',
        'is_refunded',
        'payment_id',
        'refund_id',
    )

    fieldsets = (
        ('Customer Details', {'fields': ('name', 'email', 'phone')}),
        ('Shipping Destination', {'fields': ('address1', 'address2', 'city', 'state', 'zip_code')}),
        ('Order Items & Breakdown', {'fields': ('items_json_formatted',)}),
        ('Financials & Transaction', {'fields': ('amount', 'amountpaid', 'paymentstatus', 'BookDate', 'payment_id', 'refund_id')}),
        ('Logistics & Delivery', {'fields': ('assigned_to', 'is_returned', 'delivered_at')}),
    )

    def has_add_permission(self, request):
        return False

    def order_oid_display(self, obj):
        oid = escape(obj.oid or f"ORD-{obj.id}")
        return mark_safe(
            f'<div style="font-family:monospace;font-weight:700;color:var(--color-primary-600, #4f46e5);font-size:13px;">{oid}</div>'
            f'<span style="font-size:11px;opacity:0.6;">ID: #{obj.id}</span>'
        )
    order_oid_display.short_description = "Order Reference"

    def customer_display(self, obj):
        name = escape(obj.name or "Guest")
        email = escape(obj.email or "No Email")
        return mark_safe(
            f'<strong>{name}</strong><br><span style="font-size:11px;opacity:0.75;">{email}</span>'
        )
    customer_display.short_description = "Customer"

    def amount_display(self, obj):
        amt = obj.amount or 0
        paid = obj.amountpaid or 0
        if paid > 0:
            return mark_safe(
                f'<strong style="font-size:13px;">₹{amt}</strong><br><span style="font-size:11px;color:#10b981;">Paid: ₹{paid}</span>'
            )
        return mark_safe(
            f'<strong style="font-size:13px;">₹{amt}</strong><br><span style="font-size:11px;color:#f59e0b;">Unpaid</span>'
        )
    amount_display.short_description = "Order Total"

    def payment_status_badge(self, obj):
        status = escape(str(obj.paymentstatus or "Pending"))
        if status in ["Paid", "Delivered"]:
            return mark_safe(f'<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">● {status}</span>')
        elif status in ["Pending", "Placed"]:
            return mark_safe(f'<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 animate-pulse">● {status}</span>')
        elif status == "Cancelled":
            return mark_safe('<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300">● Cancelled</span>')
        return mark_safe(f'<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300">● {status}</span>')
    payment_status_badge.short_description = "Status"

    def delivery_agent_display(self, obj):
        if obj.assigned_to:
            agent_name = escape(obj.assigned_to.get_full_name() or obj.assigned_to.username)
            return mark_safe(f'<span style="font-weight:600;color:#0284c7;">🚚 {agent_name}</span>')
        return mark_safe('<span style="color:#94a3b8;font-size:12px;">Unassigned</span>')
    delivery_agent_display.short_description = "Assigned Delivery"

    def save_model(self, request, obj, form, change):
        assigned_changed = False
        if change:
            old = Orders.objects.get(pk=obj.pk)
            assigned_changed = old.assigned_to != obj.assigned_to

        super().save_model(request, obj, form, change)

        if assigned_changed and obj.assigned_to:
            OrderUpdate.objects.create(
                order=obj,
                update_desc=f"Order assigned to delivery partner: {obj.assigned_to.username}",
                delivered=False
            )

    def items_json_formatted(self, obj):
        if not obj.items_json:
            return "-"

        data = json.loads(obj.items_json) if isinstance(obj.items_json, str) else obj.items_json
        html = ""

        for pid, values in data.items():
            qty, name, price, mrp, discount, size = values
            product_id = int(str(pid).replace("pr", "")) if str(pid).startswith("pr") else int(pid)
            product = Product.objects.filter(id=product_id).first()

            image = (
                f'<img src="{product.image.url}" loading="lazy" width="90" height="90" style="border-radius:10px;object-fit:cover;box-shadow:0 2px 8px rgba(0,0,0,0.08);">'
                if product and hasattr(product, 'image') and product.image else "—"
            )

            html += f"""
            <div style="display:flex;gap:16px;margin-bottom:12px;padding:14px;border:1px solid rgba(0,0,0,0.08);border-radius:12px;background:rgba(255,255,255,0.7);align-items:center;">
              <div style="flex-shrink:0;">{image}</div>
              <div style="flex-grow:1;">
                <b style="font-size:14px;color:#1e1b4b;">{escape(str(name))}</b><br>
                <span style="font-size:12px;color:#6366f1;font-weight:600;">Qty:</span> {qty} · 
                <span style="font-size:12px;color:#10b981;font-weight:700;">₹{price}</span> 
                <del style="font-size:11px;color:#ef4444;">₹{mrp}</del><br>
                <span style="font-size:11px;opacity:0.8;">Size: <strong>{escape(str(size))}</strong> | Discount: {escape(str(discount))}</span>
              </div>
            </div>
            """

        return mark_safe(html)

    items_json_formatted.short_description = "Ordered Items List"


# ==================== CANCELLED / REFUND ADMIN ====================

@admin.register(CancelledPaidOrder)
class CancelledPaidOrderAdmin(OrdersAdmin):
    actions = ['refund_selected_orders']

    list_display = (
        'order_oid_display',
        'customer_display',
        'amountpaid_display',
        'payment_status_badge',
        'refund_status_badge',
        'BookDate',
    )
    list_display_links = ('order_oid_display',)

    date_hierarchy = 'BookDate'
    list_filter = ('paymentstatus', 'BookDate', 'is_refunded')
    search_fields = ('oid', 'email', 'name')
    exclude = ('items_json',)

    readonly_fields = (
        'items_json_formatted',
        'amount',
        'amountpaid',
        'BookDate',
        'payment_id',
        'refund_id',
        'refund_status_badge',
    )

    fieldsets = (
        ('Customer Info', {'fields': ('name', 'email', 'phone')}),
        ('Address', {'fields': ('address1', 'address2', 'city', 'state', 'zip_code')}),
        ('Order Items', {'fields': ('items_json_formatted',)}),
        ('Payment & Amount', {'fields': ('amount', 'amountpaid', 'paymentstatus', 'BookDate')}),
        ('Refund Status & Keys', {'fields': ('refund_status_badge', 'payment_id', 'refund_id')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            paymentstatus__in=['Cancelled', 'Return Completed', 'Returned']
        )

    def amountpaid_display(self, obj):
        paid = obj.amountpaid or 0
        if paid > 0:
            return mark_safe(f'<strong style="color:#ef4444;font-size:13px;">₹{paid}</strong>')
        return mark_safe('<span style="color:#64748b;font-size:12px;">₹0 (COD / Unpaid)</span>')
    amountpaid_display.short_description = "Refundable Amount"

    def refund_status_badge(self, obj):
        if obj.is_refunded:
            return mark_safe('<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">✓ Refunded</span>')
        elif (obj.amountpaid or 0) > 0:
            return mark_safe('<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300 animate-pulse">❌ Pending Refund</span>')
        return mark_safe('<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">No Refund Required</span>')
    refund_status_badge.short_description = "Refund Status"

    def refund_selected_orders(self, request, queryset):
        for order in queryset:
            if order.is_refunded:
                messages.warning(request, f"Order {order.oid} already refunded")
                continue

            if not order.amountpaid or order.amountpaid <= 0:
                messages.info(request, f"Order {order.oid}: Amount paid is 0, no online refund needed.")
                continue

            if not order.payment_id:
                messages.warning(request, f"COD Order {order.oid}: No payment gateway transaction ID found.")
                continue

            try:
                res = refund_payment(order.payment_id, order.amountpaid)
                order.refund_id = res["id"]
                order.is_refunded = True
                order.save()

                OrderUpdate.objects.create(
                    order=order,
                    update_desc=f"Refund completed. Refund ID: {res['id']}",
                    delivered=False
                )
                messages.success(request, f"Refund successful for Order {order.oid}")
            except Exception as e:
                messages.error(request, f"Refund failed for Order {order.oid}: {str(e)}")

    refund_selected_orders.short_description = "⚡ Refund Selected Orders via Razorpay"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ==================== CONTACT ADMIN ====================

@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ('name_avatar', 'email_link', 'phone_display', 'short_desc')
    search_fields = ('name', 'email', 'phoneNo')

    def has_add_permission(self, request):
        return False

    def name_avatar(self, obj):
        name = escape(obj.name or "User")
        initials = name[:2].upper()
        return mark_safe(
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;">{initials}</div>'
            f'<strong>{name}</strong>'
            f'</div>'
        )
    name_avatar.short_description = "Customer"

    def email_link(self, obj):
        email = escape(obj.email or "")
        return mark_safe(f'<a href="mailto:{email}" style="color:#6366f1;font-weight:500;">✉️ {email}</a>')
    email_link.short_description = "Email"

    def phone_display(self, obj):
        phone = escape(obj.phoneNo or "")
        return mark_safe(f'<a href="tel:{phone}" style="color:#0284c7;">📞 {phone}</a>')
    phone_display.short_description = "Phone"

    def short_desc(self, obj):
        desc = obj.desc or ""
        return desc[:60] + "..." if len(desc) > 60 else desc
    short_desc.short_description = "Inquiry Message"