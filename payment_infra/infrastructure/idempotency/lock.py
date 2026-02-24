import redis
from django.conf import settings
from contextlib import contextmanager
import uuid


redis_client = redis.Redis.from_url(settings.REDIS_URL)


@contextmanager
def redis_lock(key: str, timeout: int = 30):
    lock_key = f"idempotency-lock:{key}"
    token = str(uuid.uuid4())

    acquired = redis_client.set(
        lock_key,
        token,
        nx=True,
        ex=timeout
    )

    try:
        if not acquired:
            raise RuntimeError("Another request is processing this idempotency key.")

        yield

    finally:
        current_token = redis_client.get(lock_key)
        if current_token and current_token.decode() == token:
            redis_client.delete(lock_key)