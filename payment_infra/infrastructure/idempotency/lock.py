"""
Module for implementing distributed locks using Redis. This is used to ensure that only one process can handle a request with a given idempotency key at a time, preventing race conditions and ensuring data consistency. The `redis_lock` context manager attempts to acquire a lock for the specified key, and if successful, allows the code block to execute. If the lock is already held by another process, it raises an exception. The lock is automatically released after the block of code is executed or if an exception occurs.
"""
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