"""
Module for the API views. This module defines the views for handling payment-related API requests, including initiating a payment charge, verifying payment callbacks, and processing payment webhooks. The PaystackPaymentView handles incoming POST requests to initiate a payment charge, validating the request data and using the PaymentService to process the payment. The PaystackCallbackView handles GET requests for verifying payment callbacks, checking the payment status and returning the appropriate response. The PaystackPaymentWebhookView is designed to handle incoming webhook events from the payment provider, validating the signature and processing the event using the WebhookService. These views are essential for managing the flow of payment-related interactions within the application, ensuring that payments are processed securely and efficiently.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.conf import settings
from payment_infra.application.services.payment_service import PaymentService
from payment_infra.infrastructure.repositories.repository import (
    PaymentRepository,
)
from payment_infra.infrastructure.providers.paystack_provider import (
    PaystackProvider,
)
from payment_infra.infrastructure.providers.registry import get_payment_service

from .serializers import PaymentRequestSerializer, PaymentResponseSerializer
from rest_framework import throttling, status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator  
from payment_infra.application.services.webhook_service import WebhookService

class PaystackPaymentView(generics.GenericAPIView):
    serializer_class = PaymentRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        service = get_payment_service()

        payment = service.process_payment(
            amount=data["amount"],
            email=data["email"],
            currency=data["currency"],
            idempotency_key=data["idempotency_key"],
            metadata={
                "email": data["email"],
                "callback_url": data["callback_url"] or settings.PAYSTACK_CALLBACK_URL,
                "plan_code": data.get("plan_code"),
            },
        )
        return Response(
            PaymentResponseSerializer(payment).data,
            status=status.HTTP_200_OK,
        )

class PaystackCallbackView(generics.GenericAPIView):

    def get(self, request, reference, *args, **kwargs):

        service = get_payment_service()
        verification_result = service.verify_payment(reference)

        if verification_result["status"]:
            return Response(
                {
                    "message": verification_result["message"],
                    "status": "success",
                    "amount": verification_result["amount"],
                    "currency": verification_result["currency"],
                    "reference": verification_result["reference"]
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Payment verification failed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

class WebhookThrottle(throttling.AnonRateThrottle):
    scope = "webhook"

@method_decorator(csrf_exempt, name='dispatch')
class PaystackPaymentWebhookView(generics.GenericAPIView):

    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [WebhookThrottle]

    def post(self, request, *args, **kwargs):

        signature = request.headers.get('x-paystack-signature')

        provider = get_payment_service().provider
        mapper = get_payment_service().mapper
        service = WebhookService(provider, mapper)

        try:
            event = service.handle(request.body, signature)
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Webhook received", "event": event
            },
            status=status.HTTP_200_OK
        )