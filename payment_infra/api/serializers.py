"""
Module for the serializers used in the payment API. This module defines the PaymentRequestSerializer and PaymentResponseSerializer classes, which are responsible for validating and serializing the data for payment requests and responses. The PaymentRequestSerializer ensures that the incoming data for a payment request is valid, including fields such as email, amount, currency, callback URL, and an optional plan code. It also generates an idempotency key to ensure that duplicate requests are handled correctly. The PaymentResponseSerializer defines the structure of the response returned after processing a payment request, including fields for status, reference, authorization URL, public key, message, and access code. These serializers play a crucial role in ensuring that the API can handle payment requests and responses in a consistent and reliable manner.
"""
from rest_framework import serializers
from django.utils import timezone
import uuid

class PaymentRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=10)
    idempotency_key = serializers.CharField(max_length=255, required=False)
    callback_url = serializers.URLField()
    plan_code = serializers.CharField(required=False, allow_null=True)

    def validate(self, attrs):
        
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        unique_id = uuid.uuid4().hex
        if not attrs.get("idempotency_key"):
            attrs["idempotency_key"] = f"trx-{unique_id}-{timestamp}"

        return attrs


class PaymentResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    reference = serializers.CharField()
    authorization_url = serializers.URLField(required=False)
    public_key = serializers.CharField()
    message = serializers.CharField()
    access_code = serializers.CharField(required=False)