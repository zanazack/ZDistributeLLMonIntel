from __future__ import annotations

import json
import platform
import socket
import uuid
from pathlib import Path

from pydantic import BaseModel, Field


def default_config_path() -> Path:
    base = Path.home() / ".zdli"
    base.mkdir(parents=True, exist_ok=True)
    return base / "edge.json"


class EdgeConfig(BaseModel):
    coordinator_url: str = ""
    enroll_token: str = ""
    worker_id: str = Field(default_factory=lambda: f"{socket.gethostname()}-{uuid.uuid4().hex[:6]}")
    site_id: str = "wan"
    openai_base_url: str | None = None
    rpc_port: int | None = None
    ram_available_mb: int = 16384

    @classmethod
    def load(cls, path: Path | None = None) -> EdgeConfig:
        p = path or default_config_path()
        if p.exists():
            return cls.model_validate(json.loads(p.read_text(encoding="utf-8")))
        cfg = cls()
        cfg.save(p)
        return cfg

    def save(self, path: Path | None = None) -> None:
        p = path or default_config_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    def os_name(self) -> str:
        return platform.system()

    def hostname(self) -> str:
        return socket.gethostname()
