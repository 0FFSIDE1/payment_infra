# payment_infra

Reusable Django payment infrastructure focused on **provider integrations**, **webhook handling**, and **idempotent payment processing**.

## Features

- Paystack payment charge + verification flow.
- Webhook processing pipeline with signature validation support.
- Idempotency infrastructure (repository + locking + in-memory helpers).
- Layered architecture (`domain`, `application`, `infrastructure`, `api`) for easier testing and extension.

## Tech Stack

- Python 3.9+
- Django 4.2+
- Django REST Framework
- Redis (for infrastructure components where configured)

## Project Layout

```text
payment_infra/
├── payment_infra/
│   ├── api/                # DRF serializers, views, URL routes
│   ├── application/        # Use-case services and interfaces
│   ├── domain/             # Domain entities
│   ├── infrastructure/     # Providers, repositories, idempotency, tasks
│   └── migrations/         # Django migrations
└── tests/                  # Unit/integration tests and Django test settings
```

## Installation

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

Using pip:

```bash
pip install -r requirements.txt
pip install -e .
```

Or with optional development dependencies:

```bash
pip install -e ".[dev]"
```

## Configuration

Set the Django settings module for local execution/tests when needed:

```bash
export DJANGO_SETTINGS_MODULE=tests.settings
```

Common environment variables used by payment providers and runtime settings include:

- `PAYSTACK_SECRET_KEY`
- `PAYSTACK_PUBLIC_KEY`
- `PAYSTACK_CALLBACK_URL`
- `PAYSTACK_WEBHOOK_SECRET`
- `DJANGO_SECRET_KEY`

> Exact usage depends on your host Django project configuration and provider setup.

## API Endpoints

Current package routes (from `payment_infra/api/urls.py`):

- `POST /paystack/charge/` — initiate a Paystack charge.
- `GET /paystack/verify/<reference>/` — verify payment status.
- `POST /payment/webhooks/` — receive payment webhooks.

### Example: initiate a charge

```bash
curl -X POST http://localhost:8000/paystack/charge/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "amount": "1000.00",
    "currency": "NGN",
    "callback_url": "https://example.com/callback"
  }'
```

## Running Tests

```bash
pytest
```

Run only integration tests:

```bash
pytest -m integration
```

## Build & Release Helpers

Makefile targets:

- `make clean`
- `make build`
- `make tag VERSION=x.y.z`
- `make release VERSION=x.y.z`

## License

MIT (see `LICENSE`).
