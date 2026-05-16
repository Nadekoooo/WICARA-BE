from __future__ import annotations

import logging

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.modules.learning.job_queue import build_media_job_queue_adapter
from app.modules.learning.service import (
    pick_next_queued_animation_job_id,
    process_animation_job_for_worker,
)

logger = logging.getLogger(__name__)


def run_media_worker() -> None:
    settings = get_settings()
    queue_adapter = build_media_job_queue_adapter(settings)
    logger.info(
        "Media worker started (queue_backend=%s, queue_key=%s).",
        settings.media_job_queue_backend,
        settings.media_jobs_queue_key,
    )

    while True:
        try:
            job_id = queue_adapter.dequeue(
                timeout_seconds=settings.media_job_dequeue_timeout_seconds
            )
        except Exception:
            logger.exception("Failed to dequeue media job, switching to db polling fallback.")
            job_id = None

        if job_id is None:
            with SessionLocal() as session:
                job_id = pick_next_queued_animation_job_id(session)

        if job_id is None:
            continue

        with SessionLocal() as session:
            processed = process_animation_job_for_worker(session, job_id=job_id)
        if not processed:
            logger.warning("Media worker failed to process job %s.", job_id)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    run_media_worker()
