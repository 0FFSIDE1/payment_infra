from django.conf import settings
from payment_infra.application.interfaces.providers import AbstractPaymentProvider


class StripeProvider(AbstractPaymentProvider):

    def charge(self, amount, currency, metadata):
        # Replace with real Stripe SDK call
        return {
            "success": True,
            "transaction_id": "mock_txn"
        }