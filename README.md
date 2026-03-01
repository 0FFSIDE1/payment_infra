# payment_infra

`payment_infra` is a reusable Django payment package that provides provider integrations, webhook handling, and idempotent payment processing logic you can plug into different Django projects.

## Why use this package?

- Reuse payment infrastructure across multiple Django services/projects.
- Start quickly with Paystack charge + verification endpoints.
- Handle webhook events through a structured service layer.
- Reduce duplicate transaction processing with idempotency support.

## Installation

### Install from PyPI

```bash
pip install payment_infra
```

### Install for local development
```bash
git clone "[repo url](https://github.com/0FFSIDE1/payment_infra.git)"
```

```bash
python -m venv venv # create a virtual environment
pip install -r requirements.txt
```

## Using `payment_infra` in any Django project

### 1) Add the app to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "payment_infra",
]
```
### 2) Configure environment variables

Typical settings used by providers/runtime:

- `PAYSTACK_SECRET_KEY`
- `PAYSTACK_PUBLIC_KEY`
- `PAYSTACK_CALLBACK_URL`
- `REDIS_URL`
- `DJANGO_SECRET_KEY`
- `CACHE_BACKEND`

> Exact variable wiring depends on your host project's Django settings.

### 3) Include the package URLs in your project urls

```python
# project/urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("payments", include("payment_infra.api.urls")),
]
```

With the example above, available endpoints become:

- `POST /payments/paystack/charge/`
- `GET /payments/paystack/verify/<reference>/`
- `POST /payments/webhooks/`

### 4) Run migrations

```bash
python manage.py migrate
```

## API example
#### Initiate payment
```bash
curl -X POST http://localhost:8000/payments/paystack/charge/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "amount": "1000.00",
    "idempotency_key": "trx-343487629495403" # optional (auto-generated if not provided)
    "currency": "NGN",
    "callback_url": "https://example.com/callback"
  }'
```
#### Verify Payment
```bash
curl -X GET 'http://localhost:8000/payments/paystack/verify/<reference>/' 
```

- Replace:
reference → with the actual reference returned from the charge endpoint.

## Package architecture

```text
payment_infra/
├── api/                # DRF serializers, views, routes
├── application/        # Service/use-case layer and interfaces
├── domain/             # Core entities
├── infrastructure/     # Providers, repositories, idempotency, tasks
└── migrations/         # Django migrations
```

This layered design keeps payment orchestration logic decoupled from API and provider implementations, making it easier to extend for additional providers or custom project requirements.

## Running tests (repository/local dev)

```bash
pytest
```

Run only integration tests:

```bash
pytest -m integration
```

Run only tests without real integration:

```bash
pytest -m "not integration"
```

## License

MIT (see `LICENSE`).
