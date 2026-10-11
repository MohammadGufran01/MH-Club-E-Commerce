from django.shortcuts import redirect
from django.conf import settings


class AuthUserRedirectMiddleware:
    """
    Middleware to prevent authenticated users from accessing auth pages
    (such as login and signup) while allowing logout and regular navigation.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        user = request.user

        # 🚨 Do not touch media and static requests
        if path.startswith(settings.MEDIA_URL) or path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        # 🚨 Never block logout requests
        logout_paths = ("/auth/logout/", "/logout/", "/admin/logout/")
        if any(path.startswith(p) for p in logout_paths):
            return self.get_response(request)

        # Prevent duplicate auth form access if user is already logged in
        duplicate_auth_paths = ("/auth/login/", "/auth/signup/")
        if user.is_authenticated and any(path.startswith(p) for p in duplicate_auth_paths):
            if user.groups.filter(name="DeliveryBoy").exists():
                return redirect("delivery_dashboard")
            if user.is_staff or user.is_superuser:
                return redirect("/admin/")
            return redirect("/")

        return self.get_response(request)
