"""
Module for the provider registry, which is responsible for returning the appropriate payment provider and event mapper based on the configuration. This module abstracts away the details of which provider is being used, allowing the rest of the application to interact with a consistent interface regardless of the underlying payment provider. The registry checks the settings to determine which provider is configured, and returns an instance of that provider along with the corresponding event mapper for handling webhooks. This design allows for easy extensibility in the future, as new providers can be added by simply implementing the required interfaces and updating the registry to return them based on configuration.
"""
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