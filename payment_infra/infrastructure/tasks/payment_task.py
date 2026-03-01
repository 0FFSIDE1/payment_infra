"""
Module for the payment processing task. This module defines a Celery task that is responsible for processing payment requests asynchronously. The task takes in the necessary parameters for processing a payment (email, amount, currency, idempotency key, and metadata) and uses the PaymentService to handle the actual payment logic. The task is configured to automatically retry on exceptions, with an exponential backoff strategy and a maximum of 5 retries. This allows for robust handling of transient errors that may occur during payment processing, such as network issues or temporary unavailability of the payment provider. The task is designed to be idempotent, ensuring that duplicate requests with the same idempotency key will not result in multiple charges.
"""
from celery import shared_task
from payment_infra.application.services.payment_service import PaymentService
from payment_infra.infrastructure.repositories.repository import PaymentRepository
from payment_infra.infrastructure.providers.registry import get_provider
from payment_infra.infrastructure.idempotency.service import IdempotencyService
from payment_infra.infrastructure.providers.registry import get_payment_service

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def process_payment_task(self, email, amount, currency, idempotency_key, metadata):
    provider = get_provider()
    repository = PaymentRepository()
    idempotency = IdempotencyService()
    service = get_payment_service(repository, provider, idempotency)

    return service.process_payment(
        email=email or metadata.get("email"),
        amount=amount,
        currency=currency,
        idempotency_key=idempotency_key,
        metadata=metadata
    )