from pathlib import Path
from django.contrib import messages
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

APPEND_SLASH = True
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# --- DEBUG PRINT TO CHECK TERMINAL ---
print("--- RAZORPAY DEBUG ---")
print("KEY_ID Loaded:", RAZORPAY_KEY_ID)
print("KEY_SECRET Loaded:", "********" if RAZORPAY_KEY_SECRET else "None/Empty")
print("----------------------")

# ======================
# BASIC SETTINGS
# ======================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = ["*"]


# ======================
# APPLICATIONS (Jazzmin removed, Unfold placed before admin)
# ======================
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'buyzoneapp',
    'authcart',
    'delivery',
]

# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'delivery.middleware.DeliveryBoyRedirectMiddleware',
    'authcart.middleware.AuthUserRedirectMiddleware',
    'buyzoneapp.middleware.GlobalExceptionMiddleware',
]

ROOT_URLCONF = 'BuyZone.urls'
WSGI_APPLICATION = 'BuyZone.wsgi.application'
ASGI_APPLICATION = 'BuyZone.asgi.application'

# ======================
# TEMPLATES
# ======================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'buyzoneapp.context_processors.global_categories',
            ],
        },
    },
]

# ======================
# DATABASE
# ======================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ======================
# PASSWORD VALIDATION
# ======================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ======================
# AUTHENTICATION BACKENDS
# ======================
AUTHENTICATION_BACKENDS = [
    'authcart.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ======================
# INTERNATIONALIZATION
# ======================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ======================
# EMAIL
# ======================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("Email")
EMAIL_HOST_PASSWORD = os.getenv("App_Password")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ======================
# STATIC & MEDIA
# ======================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ======================
# MESSAGES
# ======================
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================
# PAYMENTS
# ======================
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_RxQBw94fljOG8Y")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "qL14RIxEXO5zC7yAtWo5hqXI")

LOGIN_URL = '/auth/login/'

# ======================
# DJANGO UNFOLD – STATISTICAL & ANIMATED DASHBOARD CONFIGURATION
# ======================
from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "MH Club Admin Control Center",
    "SITE_HEADER": "MH Club Admin Suite",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "buyzoneapp.dashboard.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Analytics & Control",
                "separator": True,
                "items": [
                    {
                        "title": "Command Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Catalog & Products",
                "separator": True,
                "items": [
                    {
                        "title": "Products Catalog",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:buyzoneapp_product_changelist"),
                    },
                    {
                        "title": "Product Variants & Stock",
                        "icon": "style",
                        "link": reverse_lazy("admin:buyzoneapp_productvariant_changelist"),
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": reverse_lazy("admin:buyzoneapp_category_changelist"),
                    },
                    {
                        "title": "Subcategories",
                        "icon": "folder_special",
                        "link": reverse_lazy("admin:buyzoneapp_subcategory_changelist"),
                    },
                    {
                        "title": "Size Options",
                        "icon": "straighten",
                        "link": reverse_lazy("admin:buyzoneapp_size_changelist"),
                    },
                ],
            },
            {
                "title": "Sales & Orders",
                "separator": True,
                "items": [
                    {
                        "title": "Customer Orders",
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:buyzoneapp_orders_changelist"),
                    },
                    {
                        "title": "Refundable Orders",
                        "icon": "currency_exchange",
                        "link": reverse_lazy("admin:buyzoneapp_cancelledpaidorder_changelist"),
                    },
                    {
                        "title": "Order Timeline / Updates",
                        "icon": "published_with_changes",
                        "link": reverse_lazy("admin:buyzoneapp_orderupdate_changelist"),
                    },
                ],
            },
            {
                "title": "Logistics & Delivery",
                "separator": True,
                "items": [
                    {
                        "title": "Delivery Agents",
                        "icon": "local_shipping",
                        "link": reverse_lazy("admin:delivery_deliveryboy_changelist"),
                    },
                    {
                        "title": "Delivery OTPs",
                        "icon": "pin",
                        "link": reverse_lazy("admin:delivery_deliveryotp_changelist"),
                    },
                ],
            },
            {
                "title": "Users & Access",
                "separator": True,
                "items": [
                    {
                        "title": "Users & Customers",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "User Groups",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": "Support & Inquiries",
                "separator": True,
                "items": [
                    {
                        "title": "Customer Messages",
                        "icon": "support_agent",
                        "link": reverse_lazy("admin:buyzoneapp_contact_changelist"),
                    },
                ],
            },
            {
                "title": "Account & Session",
                "separator": True,
                "items": [
                    {
                        "title": "View Store Website",
                        "icon": "storefront",
                        "link": "/",
                    },
                    {
                        "title": "Logout",
                        "icon": "logout",
                        "link": "/auth/logout/",
                    },
                ],
            },
        ],
    },
    "ACCOUNT": {
        "navigation": [
            {
                "title": "View Store Website",
                "icon": "storefront",
                "link": "/",
            },
            {
                "title": "Logout",
                "icon": "logout",
                "link": "/auth/logout/",
            },
        ],
    },
    "STYLES": [
        lambda request: static("assets/css/admin_custom.css"),
    ],
    "SCRIPTS": [
        lambda request: static("assets/js/admin_dashboard.js"),
    ],
    "COLORS": {
        "primary": {
            "50": "238 242 255",
            "100": "224 231 255",
            "200": "199 210 254",
            "300": "165 180 252",
            "400": "129 140 248",
            "500": "99 102 241",
            "600": "79 70 229",
            "700": "67 56 202",
            "800": "55 48 163",
            "900": "49 46 129",
            "950": "30 27 75",
        },
    },
}