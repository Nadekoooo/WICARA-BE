from __future__ import annotations

import logging
import time

from app.core.config import get_settings
from app.db.session import SessionLocal, engine
from app.modules.learning.job_queue import build_media_job_queue_adapter
from app.modules.learning.service import (
    pick_next_queued_animation_job_id,
    process_animation_job_for_worker,
)

logger = logging.getLogger(__name__)


def run_media_worker() -> None:
    settings = get_settings()
    queue_adapter = build_media_job_queue_adapter(settings)
    idle_sleep_seconds = max(1, settings.media_job_dequeue_timeout_seconds)
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
            try:
                with SessionLocal() as session:
                    job_id = pick_next_queued_animation_job_id(session)
            except Exception:
                logger.exception("DB polling failed while checking queued media jobs.")
                try:
                    engine.dispose()
                except Exception:
                    logger.exception("Failed to dispose SQLAlchemy engine after polling error.")
                time.sleep(idle_sleep_seconds)
                continue

        if job_id is None:
            time.sleep(idle_sleep_seconds)
            continue

        try:
            with SessionLocal() as session:
                processed = process_animation_job_for_worker(session, job_id=job_id)
        except Exception:
            logger.exception("Unhandled worker error while processing media job %s.", job_id)
            try:
                engine.dispose()
            except Exception:
                logger.exception("Failed to dispose SQLAlchemy engine after processing error.")
            time.sleep(idle_sleep_seconds)
            continue
        if not processed:
            logger.warning("Media worker failed to process job %s.", job_id)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    run_media_worker()
