from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from buyzoneapp.views import custom_404_view

from authcart import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', auth_views.handlelogout, name='direct_logout'),
    path('', include('buyzoneapp.urls')),
    path('auth/', include('authcart.urls')),
    path("delivery/", include("delivery.urls")),
]

from django.views.static import serve

# ✅ MEDIA FILES (ALWAYS SERVED BEFORE CATCH-ALL)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Catch-all route for any unmatched URLs to always render the luxury 404 page
urlpatterns += [
    re_path(r'^.*$', custom_404_view, name='catch_all_404'),
]

handler400 = 'buyzoneapp.views.custom_400_view'
handler403 = 'buyzoneapp.views.custom_403_view'
handler404 = 'buyzoneapp.views.custom_404_view'
handler500 = 'buyzoneapp.views.custom_500_view'
