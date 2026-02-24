from celery import shared_task
from payment_infra.application.services.payment_service import PaymentService
from payment_infra.infrastructure.repositories.repository import PaymentRepository
from payment_infra.infrastructure.providers.registry import get_provider
from payment_infra.infrastructure.idempotency.service import IdempotencyService

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
    service = PaymentService(repository, provider, idempotency)

    return service.process_payment(
        email=email or metadata.get("email"),
        amount=amount,
        currency=currency,
        idempotency_key=idempotency_key,
        metadata=metadata
    )