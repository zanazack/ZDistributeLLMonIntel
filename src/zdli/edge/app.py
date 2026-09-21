from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from zdli.edge.agent import edge_agent
from zdli.edge.config import EdgeConfig, default_config_path
from zdli.web import STATIC_DIR


def create_edge_app() -> FastAPI:
    app = FastAPI(title="ZDLI Edge Client", version="0.1.0")
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def ui() -> HTMLResponse:
        return HTMLResponse((STATIC_DIR / "edge.html").read_text(encoding="utf-8"))

    @app.get("/api/config")
    def get_config() -> EdgeConfig:
        return EdgeConfig.load()

    @app.post("/api/config")
    def set_config(body: EdgeConfig) -> EdgeConfig:
        body.save()
        return body

    @app.post("/api/agent/start")
    def start_agent() -> dict[str, str]:
        edge_agent.start()
        return {"status": "started"}

    @app.post("/api/agent/stop")
    def stop_agent() -> dict[str, str]:
        edge_agent.stop()
        return {"status": "stopped"}

    @app.get("/api/agent/status")
    def agent_status() -> dict:
        return edge_agent.status()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "config": str(default_config_path())}

    return app


app = create_edge_app()
