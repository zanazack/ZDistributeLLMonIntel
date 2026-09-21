"""In-memory coordinator state (Phase 1 MVP)."""

from __future__ import annotations

import threading
import uuid
from datetime import timedelta

from zdli.schemas import GraphStatus, ModelGraph, ModelGraphUpsert, WorkerRecord, utc_now

HEARTBEAT_TTL = timedelta(seconds=45)


class CoordinatorStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._workers: dict[str, WorkerRecord] = {}
        self._graphs: dict[str, ModelGraph] = {}

    def register_worker(self, record: WorkerRecord) -> WorkerRecord:
        with self._lock:
            record.last_seen = utc_now()
            record.healthy = True
            self._workers[record.worker_id] = record
            return record

    def heartbeat(self, worker_id: str) -> WorkerRecord | None:
        with self._lock:
            w = self._workers.get(worker_id)
            if not w:
                return None
            w.last_seen = utc_now()
            w.healthy = True
            return w

    def list_workers(self) -> list[WorkerRecord]:
        with self._lock:
            self._refresh_health_locked()
            return list(self._workers.values())

    def get_worker(self, worker_id: str) -> WorkerRecord | None:
        with self._lock:
            self._refresh_health_locked()
            return self._workers.get(worker_id)

    def upsert_graph(self, body: ModelGraphUpsert) -> ModelGraph:
        with self._lock:
            ingress = self._workers.get(body.ingress_worker_id)
            ingress_url = ingress.openai_base_url if ingress else None
            graph = ModelGraph(
                **body.model_dump(),
                ingress_base_url=ingress_url,
                updated_at=utc_now(),
            )
            if graph.status == GraphStatus.ready and not ingress_url:
                graph.status = GraphStatus.degraded
            self._graphs[body.logical_model_id] = graph
            return graph

    def get_graph(self, logical_model_id: str) -> ModelGraph | None:
        with self._lock:
            g = self._graphs.get(logical_model_id)
            if not g:
                return None
            ingress = self._workers.get(g.ingress_worker_id)
            g.ingress_base_url = ingress.openai_base_url if ingress else g.ingress_base_url
            if g.status == GraphStatus.ready and not g.ingress_base_url:
                g.status = GraphStatus.degraded
            return g

    def list_model_graphs(self) -> list[ModelGraph]:
        with self._lock:
            out: list[ModelGraph] = []
            for mid in list(self._graphs.keys()):
                g = self.get_graph(mid)
                if g:
                    out.append(g)
            return out

    def create_session_id(self) -> str:
        return str(uuid.uuid4())

    def _refresh_health_locked(self) -> None:
        now = utc_now()
        for w in self._workers.values():
            if now - w.last_seen > HEARTBEAT_TTL:
                w.healthy = False


# Shared singleton for single-process MVP
store = CoordinatorStore()
