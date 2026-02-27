from rest_framework import serializers

class PaymentRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=10)
    idempotency_key = serializers.CharField(max_length=255)
    callback_url = serializers.URLField()
    plan_code = serializers.CharField(required=False, allow_null=True)


class PaymentResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    reference = serializers.CharField()
    authorization_url = serializers.URLField(required=False)
    public_key = serializers.CharField()
    message = serializers.CharField()
    access_code = serializers.CharField(required=False)