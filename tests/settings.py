from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "test-secret-key")
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "payment_infra",
    "rest_framework",
    
]

CACHES = {
    "default": {
        "BACKEND": os.getenv("CACHE_BACKEND", "django.core.cache.backends.locmem.LocMemCache"),
    }
}

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = []


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "webhook": "30/minute",
    },
}

PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "test-secret-key")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY", "test-public-key")
PAYSTACK_CALLBACK_URL = os.getenv("PAYSTACK_CALLBACK_URL", "http://localhost:8000/paystack/callback/")
ROOT_URLCONF = "payment_infra.api.urls"