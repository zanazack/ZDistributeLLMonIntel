"""Simple interval scheduler for control center."""

from __future__ import annotations

import threading
import uuid
from datetime import timedelta

from zdli.schemas import ScheduledJob, ScheduledJobCreate, utc_now


class JobScheduler:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._jobs: dict[str, ScheduledJob] = {}

    def add(self, body: ScheduledJobCreate) -> ScheduledJob:
        with self._lock:
            jid = str(uuid.uuid4())
            now = utc_now()
            job = ScheduledJob(
                id=jid,
                **body.model_dump(),
                last_run=None,
                next_run=now + timedelta(minutes=body.interval_minutes),
            )
            self._jobs[jid] = job
            return job

    def list_jobs(self) -> list[ScheduledJob]:
        with self._lock:
            return list(self._jobs.values())

    def tick(self) -> list[tuple[str, str]]:
        """Return list of (job_id, action) that fired."""
        fired: list[tuple[str, str]] = []
        now = utc_now()
        with self._lock:
            for job in self._jobs.values():
                if not job.enabled or not job.next_run:
                    continue
                if now >= job.next_run:
                    fired.append((job.id, job.action))
                    job.last_run = now
                    job.next_run = now + timedelta(minutes=job.interval_minutes)
                    job.last_result = "ok"
        return fired


job_scheduler = JobScheduler()
