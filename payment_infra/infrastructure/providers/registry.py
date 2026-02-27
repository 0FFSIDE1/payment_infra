from django.conf import settings
from payment_infra.infrastructure.providers.stripe_provider import StripeProvider
from payment_infra.infrastructure.providers.paystack_provider import PaystackProvider
from payment_infra.infrastructure.repositories.repository import PaymentRepository
from payment_infra.infrastructure.idempotency.service import IdempotencyService
from payment_infra.application.services.payment_service import PaymentService
from payment_infra.application.webhooks.event_mapper import PaystackEventMapper

DEFAULTS = {
    "PROVIDER": "paystack",
}

def get_setting(name):
    return getattr(settings, f"DJANGO_PAYMENTS_{name}", DEFAULTS.get(name))


def get_provider():
    provider_path = get_setting("PROVIDER").lower()

    if provider_path == "stripe":
        # Future: return StripeProvider()
        raise NotImplementedError("Stripe mapper not implemented yet")
        
    if provider_path == "paystack":
        return PaystackProvider()

    raise ValueError("Unsupported payment provider")

def get_mapper():
    provider_path = get_setting("PROVIDER").lower()

    if provider_path == "paystack":
        return PaystackEventMapper()
    
    if provider_path == "stripe":
        # Future: return StripeEventMapper()
        raise NotImplementedError("Stripe mapper not implemented yet")

    # Future: add mappers for other providers here

def get_payment_service():
    return PaymentService(
        repository=PaymentRepository(),
        provider=get_provider(),
        idempotency_service=IdempotencyService(),
        mapper=get_mapper(),
    )