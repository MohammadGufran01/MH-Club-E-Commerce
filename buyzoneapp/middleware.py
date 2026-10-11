import logging
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.conf import settings

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware:
    """
    Catches 400, 403, 404, and unhandled 500 exceptions across all views
    and renders graceful, luxury-styled error pages or JSON responses for API calls.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Do not override static files or media files
        if request.path.startswith(settings.STATIC_URL) or (settings.MEDIA_URL and request.path.startswith(settings.MEDIA_URL)):
            return response

        # Intercept 400, 403, 404, 500 error status codes
        if response.status_code == 404:
            return render(request, "404.html", status=404)
        elif response.status_code == 403:
            return render(request, "403.html", status=403)
        elif response.status_code == 400:
            return render(request, "400.html", status=400)
        elif response.status_code == 500:
            return render(request, "500.html", status=500)

        return response

    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception on {request.path}: {str(exception)}", exc_info=True)

        # Return JSON for AJAX/API endpoints
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or request.path.startswith("/api/")
            or request.content_type == "application/json"
        ):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "An unexpected server error occurred. Please try again.",
                    "error_type": exception.__class__.__name__
                },
                status=500
            )

        if isinstance(exception, Http404):
            return render(request, "404.html", status=404)
        elif isinstance(exception, PermissionDenied):
            return render(request, "403.html", status=403)
        elif isinstance(exception, SuspiciousOperation):
            return render(request, "400.html", status=400)

        # Render customer-friendly, professional 500 error page
        return render(request, "500.html", status=500)
