from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = "test-secret-key"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "payment_infra",
    "rest_framework",
]

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

PAYSTACK_BASE_URL = "https://api.paystack.co"
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
PAYSTACK_CALLBACK_URL = "https://example.com/callback"
ROOT_URLCONF = "payment_infra.api.urls"