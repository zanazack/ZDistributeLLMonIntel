from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse

from zdli.schemas import (
    REFERENCE_LOGICAL_MODEL,
    OpenAIModelCard,
    OpenAIModelList,
)
from zdli.settings import GatewaySettings

settings = GatewaySettings()


def verify_gateway_key(authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bearer API key required")
    key = authorization.removeprefix("Bearer ").strip()
    if key != settings.api_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid API key")


def create_app() -> FastAPI:
    app = FastAPI(title="ZDLI OpenAI Gateway", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/v1/models")
    async def list_models(authorization: str | None = Header(default=None)) -> OpenAIModelList:
        verify_gateway_key(authorization)
        graphs = await _fetch_graphs()
        data = [
            OpenAIModelCard(id=g["logical_model_id"])
            for g in graphs
            if g.get("status") in ("ready", "degraded") and g.get("ingress_base_url")
        ]
        if not data:
            data = [OpenAIModelCard(id=REFERENCE_LOGICAL_MODEL)]
        return OpenAIModelList(data=data)

    @app.post("/v1/chat/completions")
    async def chat_completions(
        request: Request,
        authorization: str | None = Header(default=None),
    ) -> Any:
        verify_gateway_key(authorization)
        body = await request.json()
        model = body.get("model")
        if not model:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "model is required")

        ingress = await _resolve_ingress(model)
        stream = bool(body.get("stream", False))
        url = f"{ingress.rstrip('/')}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}

        if stream:
            return StreamingResponse(
                _stream_proxy(url, body, headers),
                media_type="text/event-stream",
            )

        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
            resp = await client.post(url, json=body, headers=headers)
        if resp.status_code >= 400:
            raise HTTPException(resp.status_code, resp.text)
        return JSONResponse(content=resp.json())

    return app


async def _fetch_graphs() -> list[dict[str, Any]]:
    url = f"{settings.coordinator_url.rstrip('/')}/zdl/v1/graphs"
    headers = {"Authorization": f"Bearer {settings.coordinator_token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
    if resp.status_code >= 400:
        return []
    return resp.json()


async def _resolve_ingress(logical_model_id: str) -> str:
    url = f"{settings.coordinator_url.rstrip('/')}/zdl/v1/sessions"
    headers = {"Authorization": f"Bearer {settings.coordinator_token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            url,
            params={"logical_model_id": logical_model_id},
            headers=headers,
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            f"Fabric unavailable for model {logical_model_id}: {resp.text}",
        )
    data = resp.json()
    return data["ingress_base_url"]


async def _stream_proxy(url: str, body: dict[str, Any], headers: dict[str, str]):
    async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
        async with client.stream("POST", url, json=body, headers=headers) as resp:
            if resp.status_code >= 400:
                detail = await resp.aread()
                yield f"data: {json.dumps({'error': detail.decode()})}\n\n"
                return
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk


app = create_app()
