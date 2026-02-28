
# payment_infra

Lightweight Django-based payment infrastructure and provider integrations (Paystack, Stripe) for processing payments, handling webhooks, and providing idempotency controls.

## Key Features

- Provider-agnostic payment service with pluggable providers.
- Webhook handling and event mapping.
- In-memory idempotency helpers for safe retry and deduplication.
- Clear application/service/repository separation for testability.

## Table of Contents

- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [Running the app](#running-the-app)
- [Running tests](#running-tests)
- [Where to look in the codebase](#where-to-look-in-the-codebase)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

Top-level package: `payment_infra`.

- `payment_infra/api/` — Django REST API layer (serializers, views, urls).
- `payment_infra/application/` — Application services and interfaces.
- `payment_infra/domain/` — Domain entities and business models.
- `payment_infra/infrastructure/` — Providers, repositories, idempotency helpers, background tasks.
- `tests/` — Unit and integration tests.

See the code for details and entry points.

## Requirements

- Python 3.9+ (project uses `pyproject.toml`).
- Virtual environment (recommended).
- Optional: `poetry` if you prefer to use it for dependency management.

## Quickstart

1. Create and activate a virtual environment:

```
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
.venv\\Scripts\\activate     # Windows (Powershell)
```

2. Install dependencies (choose one):

```
# Using pip editable install (recommended for development)
pip install -e .

# Or with poetry
poetry install
```

3. Prepare environment variables.

The project expects typical payment integration settings. Common environment variables:

- `DATABASE_URL` — database connection URL (if using an external DB).
- `STRIPE_SECRET_KEY` — Stripe secret key (if using Stripe provider).
- `PAYSTACK_SECRET_KEY` — Paystack secret key (if using Paystack provider).
- `DJANGO_SECRET_KEY` — Django secret key.

Create a `.env` or set these in your environment. The exact variable names may vary depending on your Django settings file in `tests/settings.py` and your deployment configuration.

4. Apply migrations and create any necessary local DB:

```
python manage.py migrate
```

5. Run the development server:

```
python manage.py runserver
```

## Running tests

Run the test suite with `pytest` (project includes a `pytest.ini`):

```
pytest -q
```

If you added or changed providers or services, run the focused tests in `tests/` to validate behaviour.

## Usage / API

The repository exposes a Django REST API (see `payment_infra/api/`). Typical endpoints for a payment system include creating payments and receiving webhooks. Example `curl` usage (adjust paths if your project mounts the API under a different prefix):

```
# Create a payment (example)
curl -X POST http://127.0.0.1:8000/api/payments/ \\
	-H "Content-Type: application/json" \\
	-d '{"amount":1000, "currency":"NGN", "provider":"paystack", "metadata": {"order_id":"1234"}}'

# Webhook endpoint (provider POSTs here)
curl -X POST http://127.0.0.1:8000/api/webhooks/paystack/ \\
	-H "Content-Type: application/json" \\
	-d @sample_webhook.json
```

Adjust payloads and URLs to match the actual `urls.py` routing in `payment_infra/api/urls.py`.

## Where to look in the codebase

- Service layer: [payment_infra/application/services/payment_service.py](payment_infra/application/services/payment_service.py)
- Webhook handling: [payment_infra/application/services/webhook_service.py](payment_infra/application/services/webhook_service.py)
- Provider implementations: [payment_infra/infrastructure/providers/paystack_provider.py](payment_infra/infrastructure/providers/paystack_provider.py) and [payment_infra/infrastructure/providers/stripe_provider.py](payment_infra/infrastructure/providers/stripe_provider.py)
- Provider registry: [payment_infra/infrastructure/providers/registry.py](payment_infra/infrastructure/providers/registry.py)
- Idempotency utilities: [payment_infra/infrastructure/idempotency/](payment_infra/infrastructure/idempotency/)
- API layer: [payment_infra/api/](payment_infra/api/)

## Background tasks

There are task helpers in `payment_infra/infrastructure/tasks/` such as `payment_task.py`. Inspect them to see how asynchronous or scheduled work is expected to run in your environment.

## Development notes

- The codebase separates interfaces (contracts) from concrete implementations to make testing and provider swaps easier.
- Use the test-suite (`tests/`) as examples for expected behaviour and typical payloads.

## Contributing

1. Fork the repository and create a feature branch.
2. Run tests and linters locally.
3. Open a pull request with a clear description and tests for new behaviour.

## License

This project includes a `LICENSE` file at the repository root. See that file for license details.

---

If you'd like, I can also:

- Run the test suite and report failures.
- Extract precise API routes and example payloads from `payment_infra/api/urls.py` and `payment_infra/api/serializers.py` and add concrete curl examples.
- Add a `.env.example` with the environment variables used by tests and settings.

Tell me which follow-up you'd like next.
