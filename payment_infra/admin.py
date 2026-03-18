from django.contrib import admin

from .domain.entities.models import Payment, PaymentWebhookLog

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("amount", "currency", "email", "status", "idempotency_key", "created_at")
    search_fields = ("email", "amount", "status", "idempotency_key")

@admin.register(PaymentWebhookLog)
class PaymentWebhookLogAdmin(admin.ModelAdmin):
    list_display = ("event", "invoice_code", "reference", "subscription_code", "received_at", "processed", "valid_signature")
    search_fields = ("event", "invoice_code", "processed")

