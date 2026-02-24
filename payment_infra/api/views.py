from rest_framework import generics, status
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