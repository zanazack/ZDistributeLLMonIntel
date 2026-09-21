from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query, status

from zdli.auth import verify_admin, verify_worker_or_admin
from zdli.schemas import (
    ModelGraph,
    ModelGraphUpsert,
    SessionCreateResponse,
    WorkerRecord,
    WorkerRegisterRequest,
    WorkerStatusUpdate,
)
from zdli.store import CoordinatorStore, store


def create_app(coordinator_store: CoordinatorStore | None = None) -> FastAPI:
    app = FastAPI(title="ZDLI Coordinator", version="0.1.0")
    db = coordinator_store or store

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/zdl/v1/workers/register",
        response_model=WorkerRecord,
        dependencies=[Depends(verify_worker_or_admin)],
    )
    def register_worker(body: WorkerRegisterRequest) -> WorkerRecord:
        record = WorkerRecord(**body.model_dump())
        return db.register_worker(record)

    @app.post(
        "/zdl/v1/workers/{worker_id}/heartbeat",
        response_model=WorkerRecord,
        dependencies=[Depends(verify_worker_or_admin)],
    )
    def heartbeat(worker_id: str) -> WorkerRecord:
        w = db.heartbeat(worker_id)
        if not w:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Worker not registered")
        return w

    @app.get(
        "/zdl/v1/workers",
        response_model=list[WorkerRecord],
        dependencies=[Depends(verify_admin)],
    )
    def list_workers() -> list[WorkerRecord]:
        return db.list_workers()

    @app.put(
        "/zdl/v1/graphs/{logical_model_id}",
        response_model=ModelGraph,
        dependencies=[Depends(verify_admin)],
    )
    def upsert_graph(logical_model_id: str, body: ModelGraphUpsert) -> ModelGraph:
        if body.logical_model_id != logical_model_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "logical_model_id mismatch")
        for stage in body.stages:
            if not db.get_worker(stage.worker_id):
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    f"Unknown worker_id in stage: {stage.worker_id}",
                )
        if not db.get_worker(body.ingress_worker_id):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Unknown ingress worker: {body.ingress_worker_id}",
            )
        return db.upsert_graph(body)

    @app.get(
        "/zdl/v1/graphs/{logical_model_id}",
        response_model=ModelGraph,
        dependencies=[Depends(verify_admin)],
    )
    def get_graph(logical_model_id: str) -> ModelGraph:
        g = db.get_graph(logical_model_id)
        if not g:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Graph not found")
        return g

    @app.get(
        "/zdl/v1/graphs",
        response_model=list[ModelGraph],
        dependencies=[Depends(verify_admin)],
    )
    def list_graphs() -> list[ModelGraph]:
        return db.list_model_graphs()

    @app.post(
        "/zdl/v1/sessions",
        response_model=SessionCreateResponse,
        dependencies=[Depends(verify_admin)],
    )
    def create_session(
        logical_model_id: str = Query(..., min_length=1),
    ) -> SessionCreateResponse:
        g = db.get_graph(logical_model_id)
        if not g:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Model graph not found")
        if not g.ingress_base_url:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "Ingress worker has no openai_base_url; start llama-server on ingress node",
            )
        if g.status.value not in ("ready", "degraded"):
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"Graph status: {g.status}")
        return SessionCreateResponse(
            session_id=db.create_session_id(),
            logical_model_id=g.logical_model_id,
            ingress_base_url=g.ingress_base_url.rstrip("/"),
            stage_count=len(g.stages),
        )

    @app.patch(
        "/zdl/v1/workers/{worker_id}/status",
        response_model=WorkerRecord,
        dependencies=[Depends(verify_worker_or_admin)],
    )
    def update_status(worker_id: str, body: WorkerStatusUpdate) -> WorkerRecord:
        w = db.update_worker_status(worker_id, body.phase, body.status_message)
        if not w:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Worker not registered")
        return w

    return app


app = create_app()
