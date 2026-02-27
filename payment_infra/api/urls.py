from django.urls import path
from .views import PaystackPaymentView, PaystackCallbackView, PaystackPaymentWebhookView

urlpatterns = [
    path("paystack/charge/", PaystackPaymentView.as_view(), name="paystack-charge"),
    path("paystack/verify/<str:reference>/", PaystackCallbackView.as_view(), name="paystack-verify"),
    path("payment/webhooks/", PaystackPaymentWebhookView.as_view(), name="payment-webhook"),
]