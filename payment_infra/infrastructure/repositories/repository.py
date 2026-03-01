from payment_infra.domain.entities.models import Payment as PaymentModel
from payment_infra.domain.entities.payment import Payment


class PaymentRepository:

    def create(self, payment: Payment) -> Payment:
        PaymentModel.objects.create(
            id=payment.id,
            email=payment.email,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            idempotency_key=payment.idempotency_key,
        )
        return payment

    def get_by_idempotency_key(self, key: str):
        try:
            obj = PaymentModel.objects.get(idempotency_key=key)
            return obj
        except PaymentModel.DoesNotExist:
            return None

    def update_status(self, payment_id, status):
        PaymentModel.objects.filter(id=payment_id).update(status=status)