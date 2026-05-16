from __future__ import annotations

import logging
from typing import Protocol
from uuid import UUID

from app.core.config import Settings, get_settings

try:
    import redis
except ImportError:  # pragma: no cover - runtime optional dependency
    redis = None

logger = logging.getLogger(__name__)


class MediaJobQueueAdapter(Protocol):
    def enqueue(self, *, job_id: UUID) -> None:
        ...

    def dequeue(self, *, timeout_seconds: int) -> UUID | None:
        ...


class NoopMediaJobQueueAdapter:
    def enqueue(self, *, job_id: UUID) -> None:
        logger.debug("Queue backend is noop, skip enqueue for media job %s.", job_id)

    def dequeue(self, *, timeout_seconds: int) -> UUID | None:
        return None


class RedisMediaJobQueueAdapter:
    def __init__(self, *, redis_url: str, queue_key: str) -> None:
        if redis is None:
            raise RuntimeError(
                "Redis queue backend requires dependency 'redis'. Install it with pip install redis."
            )
        self._queue_key = queue_key
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)

    def enqueue(self, *, job_id: UUID) -> None:
        self._client.rpush(self._queue_key, str(job_id))

    def dequeue(self, *, timeout_seconds: int) -> UUID | None:
        result = self._client.blpop(self._queue_key, timeout=timeout_seconds)
        if result is None:
            return None
        _, payload = result
        try:
            return UUID(str(payload))
        except ValueError:
            logger.warning("Dropped invalid media job id payload from queue: %s", payload)
            return None


def build_media_job_queue_adapter(settings: Settings | None = None) -> MediaJobQueueAdapter:
    resolved = settings or get_settings()
    if resolved.media_job_queue_backend == "noop":
        return NoopMediaJobQueueAdapter()
    return RedisMediaJobQueueAdapter(
        redis_url=resolved.redis_url,
        queue_key=resolved.media_jobs_queue_key,
    )
