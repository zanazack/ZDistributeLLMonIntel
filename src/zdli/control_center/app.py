from __future__ import annotations

import json
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from zdli.auth import verify_admin
from zdli.coordinator.app import create_app as create_coordinator_app
from zdli.scheduler import job_scheduler
from zdli.schemas import (
    REFERENCE_LOGICAL_MODEL,
    ClusterInfo,
    GraphStatus,
    ModelGraphUpsert,
    ScheduledJobCreate,
    ShardStage,
)
from zdli.settings import CoordinatorSettings
from zdli.store import store
from zdli.web import STATIC_DIR

_cluster_urls: dict[str, str] = {}
_CONFIG_FILE = Path.home() / ".zdli" / "control-center.json"


def _load_urls() -> None:
    global _cluster_urls
    settings = CoordinatorSettings()
    if _CONFIG_FILE.exists():
        _cluster_urls = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
    if not _cluster_urls.get("public_coordinator_url"):
        base = settings.public_url or f"http://127.0.0.1:{settings.port}"
        _cluster_urls.setdefault("public_coordinator_url", base)
        _cluster_urls.setdefault("public_gateway_url", "http://127.0.0.1:8080")


def _save_urls() -> None:
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(_cluster_urls, indent=2), encoding="utf-8")


def create_control_app() -> FastAPI:
    _load_urls()
    app = create_coordinator_app(store)
    app.title = "ZDLI Control Center"

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/ui", response_class=HTMLResponse)
    @app.get("/", response_class=HTMLResponse)
    def ui_root() -> HTMLResponse:
        return HTMLResponse((STATIC_DIR / "control.html").read_text(encoding="utf-8"))

    @app.get("/api/cluster/info", response_model=ClusterInfo)
    def cluster_info(_: None = Depends(verify_admin)) -> ClusterInfo:
        workers = store.list_workers()
        healthy = sum(1 for w in workers if w.healthy)
        settings = CoordinatorSettings()
        return ClusterInfo(
            public_coordinator_url=_cluster_urls.get("public_coordinator_url", ""),
            public_gateway_url=_cluster_urls.get("public_gateway_url", ""),
            enroll_token_hint=settings.enroll_token[:4] + "… (see Control Center env / installer output)",
            worker_count=len(workers),
            healthy_workers=healthy,
            platform_note="Edge nodes connect outbound to public coordinator URL (WAN/corporate firewall friendly).",
        )

    @app.get("/api/cluster/enroll-token")
    def get_enroll_token(_: None = Depends(verify_admin)) -> dict[str, str]:
        return {"enroll_token": CoordinatorSettings().enroll_token}

    @app.post("/api/cluster/public-urls")
    def set_public_urls(body: dict[str, str], _: None = Depends(verify_admin)) -> dict[str, str]:
        _cluster_urls["public_coordinator_url"] = body.get("public_coordinator_url", "").strip()
        _cluster_urls["public_gateway_url"] = body.get("public_gateway_url", "").strip()
        _save_urls()
        return _cluster_urls

    @app.get("/api/schedule")
    def list_schedule(_: None = Depends(verify_admin)):
        job_scheduler.tick()
        return job_scheduler.list_jobs()

    @app.post("/api/schedule")
    def add_schedule(body: ScheduledJobCreate, _: None = Depends(verify_admin)):
        return job_scheduler.add(body)

    @app.post("/api/cluster/bootstrap-graph")
    def bootstrap_graph(_: None = Depends(verify_admin)) -> dict[str, str]:
        workers = store.list_workers()
        if len(workers) < 1:
            return {"error": "Need at least one registered worker"}
        ids = [w.worker_id for w in workers]
        ingress = ids[-1]
        stages = [ShardStage(stage_index=i, worker_id=w) for i, w in enumerate(ids)]
        graph = ModelGraphUpsert(
            logical_model_id=REFERENCE_LOGICAL_MODEL,
            ingress_worker_id=ingress,
            stages=stages,
            status=GraphStatus.ready,
        )
        store.upsert_graph(graph)
        return {"status": "ok", "logical_model_id": REFERENCE_LOGICAL_MODEL, "stages": str(len(stages))}

    return app
