from __future__ import annotations

import signal
import sys
import time

import httpx

from zdli.schemas import WorkerRegisterRequest
from zdli.settings import WorkerSettings


def register(settings: WorkerSettings) -> None:
    body = WorkerRegisterRequest(
        worker_id=settings.worker_id,
        site_id=settings.site_id,
        runtimes=["llama.cpp-rpc"],
        ram_available_mb=settings.ram_available_mb,
        rpc_host=settings.rpc_host,
        rpc_port=settings.rpc_port,
        openai_base_url=settings.openai_base_url,
    )
    url = f"{settings.coordinator_url.rstrip('/')}/zdl/v1/workers/register"
    headers = {"Authorization": f"Bearer {settings.coordinator_token}"}
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, json=body.model_dump(), headers=headers)
        resp.raise_for_status()


def heartbeat(settings: WorkerSettings) -> None:
    url = f"{settings.coordinator_url.rstrip('/')}/zdl/v1/workers/{settings.worker_id}/heartbeat"
    headers = {"Authorization": f"Bearer {settings.coordinator_token}"}
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=headers)
        resp.raise_for_status()


def main() -> None:
    settings = WorkerSettings()
    stop = False

    def _stop(*_: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _stop)

    register(settings)
    print(f"zdl-worker: registered {settings.worker_id} site={settings.site_id}", flush=True)

    while not stop:
        try:
            heartbeat(settings)
        except httpx.HTTPError as exc:
            print(f"zdl-worker: heartbeat failed: {exc}", file=sys.stderr, flush=True)
        time.sleep(settings.heartbeat_seconds)

    print("zdl-worker: stopped", flush=True)


if __name__ == "__main__":
    main()
