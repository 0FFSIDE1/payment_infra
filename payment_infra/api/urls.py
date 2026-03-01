"""
Module for the API URLs. This module defines the URL patterns for the payment API, including endpoints for initiating a payment charge, verifying a payment callback, and handling payment webhooks etc. The URLs are mapped to their respective views, which handle the logic for processing payment requests, verifying payment statuses, and managing webhook events from the payment provider. This module serves as the entry point for clients interacting with the payment API, providing a structured way to access the various functionalities related to payment processing.
"""
from django.urls import path
from .views import PaystackPaymentView, PaystackCallbackView, PaystackPaymentWebhookView

urlpatterns = [
    path("paystack/charge/", PaystackPaymentView.as_view(), name="paystack-charge"),
    path("paystack/verify/<str:reference>/", PaystackCallbackView.as_view(), name="paystack-verify"),
    path("webhooks/", PaystackPaymentWebhookView.as_view(), name="payment-webhook"),
]