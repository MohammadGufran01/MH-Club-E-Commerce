from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

# Unregister default admin registrations
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('username_avatar', 'email', 'first_name', 'last_name', 'role_badge', 'is_active_badge')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def username_avatar(self, obj):
        initials = (obj.first_name[:1] + obj.last_name[:1]) if (obj.first_name and obj.last_name) else obj.username[:2]
        uname = escape(obj.username or "")
        return mark_safe(
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'<div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;">{initials.upper()}</div>'
            f'<strong>{uname}</strong>'
            f'</div>'
        )
    username_avatar.short_description = "User"

    def role_badge(self, obj):
        if obj.is_superuser:
            return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300">👑 Superuser</span>')
        elif obj.is_staff:
            return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">🛡️ Staff</span>')
        return mark_safe('<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300">👤 Customer</span>')
    role_badge.short_description = "Role"

    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color:#10b981;font-weight:600;">● Active</span>')
        return mark_safe('<span style="color:#ef4444;font-weight:600;">● Disabled</span>')
    is_active_badge.short_description = "Status"


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
