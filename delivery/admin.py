from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from .models import DeliveryBoy, DeliveryOTP
from buyzoneapp.models import Orders


@admin.register(DeliveryBoy)
class DeliveryBoyAdmin(ModelAdmin):
    list_display = ('id', 'agent_display', 'phone_display', 'active_orders_count', 'status_badge')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    list_filter = ('user__is_active',)

    def agent_display(self, obj):
        name = escape(obj.user.get_full_name() or obj.user.username)
        email = escape(obj.user.email or "No email")
        initials = name[:2].upper()
        return mark_safe(
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;">{initials}</div>'
            f'<div><strong style="color:var(--color-primary-600, #4f46e5);">{name}</strong><br><span style="font-size:12px;opacity:0.7;">{email}</span></div>'
            f'</div>'
        )
    agent_display.short_description = "Delivery Agent"

    def phone_display(self, obj):
        phone = escape(obj.phone or "")
        return mark_safe(f'<a href="tel:{phone}" style="color:#0284c7;font-weight:500;">📞 {phone}</a>')
    phone_display.short_description = "Phone Number"

    def active_orders_count(self, obj):
        count = Orders.objects.filter(assigned_to=obj.user, delivered_at__isnull=True).count()
        return mark_safe(f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300">{count} Active</span>')
    active_orders_count.short_description = "Active Assignments"

    def status_badge(self, obj):
        if obj.user.is_active:
            return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">● Active</span>')
        return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300">● Inactive</span>')
    status_badge.short_description = "Status"


@admin.register(DeliveryOTP)
class DeliveryOTPAdmin(ModelAdmin):
    list_display = ('id', 'order_link', 'otp_badge', 'verified_badge', 'created_at', 'expiry_badge')
    list_filter = ('verified', 'created_at')
    search_fields = ('order__oid', 'order__id', 'otp')
    readonly_fields = ('created_at',)

    def order_link(self, obj):
        oid = escape(obj.order.oid if obj.order and obj.order.oid else "N/A")
        oid_num = obj.order.id if obj.order else "N/A"
        return mark_safe(f'<strong>Order #{oid_num} ({oid})</strong>')
    order_link.short_description = "Associated Order"

    def otp_badge(self, obj):
        otp = escape(str(obj.otp or ""))
        return mark_safe(f'<span style="font-family:monospace;font-size:14px;letter-spacing:2px;font-weight:700;padding:2px 8px;border-radius:6px;background:rgba(99,102,241,0.1);color:#6366f1;">{otp}</span>')
    otp_badge.short_description = "OTP Code"

    def verified_badge(self, obj):
        if obj.verified:
            return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">✓ Verified</span>')
        return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">⏳ Pending</span>')
    verified_badge.short_description = "Verification"

    def expiry_badge(self, obj):
        if obj.is_expired():
            return mark_safe('<span style="color:#ef4444;font-size:12px;font-weight:600;">Expired</span>')
        return mark_safe('<span style="color:#10b981;font-size:12px;font-weight:600;">Valid</span>')
    expiry_badge.short_description = "Validity"
