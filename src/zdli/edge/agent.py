from __future__ import annotations

import threading
import time
from collections import deque

import httpx

from zdli.edge.config import EdgeConfig
from zdli.schemas import WorkerPhase, WorkerRegisterRequest, WorkerStatusUpdate


def _ram_available_mb() -> int:
    try:
        import shutil

        total, _used, free = shutil.disk_usage("/")  # noqa: not RAM but avoid extra deps on MVP
        _ = total
        return max(8192, int(free / (1024 * 1024)))
    except Exception:
        return 16384


class EdgeAgent:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._log: deque[str] = deque(maxlen=200)
        self.phase = "offline"
        self.message = ""
        self.connected = False
        self._config = EdgeConfig.load()

    def log(self, line: str) -> None:
        self._log.append(line)

    def status(self) -> dict:
        return {
            "phase": self.phase,
            "message": self.message,
            "connected": self.connected,
            "log": list(self._log),
        }

    def reload_config(self) -> None:
        self._config = EdgeConfig.load()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self.phase = "offline"
        self.connected = False
        self.message = "Stopped by user"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._config.enroll_token}"}

    def _run(self) -> None:
        self.reload_config()
        if not self._config.coordinator_url or not self._config.enroll_token:
            self.phase = "error"
            self.message = "Set coordinator URL and enroll token in the UI"
            return

        base = self._config.coordinator_url.rstrip("/")
        self.phase = "configuring"
        self.message = "Registering with coordinator…"
        self.log(f"Connecting to {base}")

        body = WorkerRegisterRequest(
            worker_id=self._config.worker_id,
            site_id=self._config.site_id,
            hostname=self._config.hostname(),
            os_name=self._config.os_name(),
            ram_available_mb=self._config.ram_available_mb or _ram_available_mb(),
            rpc_port=self._config.rpc_port,
            openai_base_url=self._config.openai_base_url,
            phase=WorkerPhase.configuring,
            status_message="Edge agent started",
        )
        try:
            with httpx.Client(timeout=60.0, trust_env=True) as client:
                r = client.post(
                    f"{base}/zdl/v1/workers/register",
                    json=body.model_dump(),
                    headers=self._headers(),
                )
                r.raise_for_status()
                self.connected = True
                self.phase = "ready"
                self.message = "Registered; sending heartbeats"
                self.log("Registration OK")

                while not self._stop.is_set():
                    try:
                        hb = client.post(
                            f"{base}/zdl/v1/workers/{self._config.worker_id}/heartbeat",
                            headers=self._headers(),
                        )
                        hb.raise_for_status()
                        self.phase = "ready"
                        self.message = f"Last heartbeat OK ({self._config.os_name()})"
                    except httpx.HTTPError as exc:
                        self.phase = "error"
                        self.message = str(exc)
                        self.log(f"Heartbeat error: {exc}")

                    status = WorkerStatusUpdate(
                        phase=WorkerPhase.ready if self.phase == "ready" else WorkerPhase.error,
                        status_message=self.message,
                    )
                    try:
                        client.patch(
                            f"{base}/zdl/v1/workers/{self._config.worker_id}/status",
                            json=status.model_dump(),
                            headers=self._headers(),
                        )
                    except httpx.HTTPError:
                        pass

                    self._stop.wait(15)
        except httpx.HTTPError as exc:
            self.connected = False
            self.phase = "error"
            self.message = str(exc)
            self.log(f"Registration failed: {exc}")


edge_agent = EdgeAgent()
