"""ZDLI v0.1 control-plane schemas."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


REFERENCE_LOGICAL_MODEL = "intel-distributed-qwen2.5-32b-instruct-q4"


class GraphStatus(str, Enum):
    draft = "draft"
    ready = "ready"
    degraded = "degraded"


class WorkerPhase(str, Enum):
    pending = "pending"
    installing = "installing"
    configuring = "configuring"
    ready = "ready"
    running = "running"
    error = "error"


class WorkerRegisterRequest(BaseModel):
    worker_id: str = Field(..., min_length=1, max_length=128)
    site_id: str = Field(default="default", max_length=64)
    hostname: str = Field(default="", max_length=256)
    os_name: str = Field(default="", max_length=64)
    runtimes: list[str] = Field(default_factory=lambda: ["llama.cpp-rpc"])
    ram_available_mb: int = Field(default=0, ge=0)
    phase: WorkerPhase = WorkerPhase.configuring
    status_message: str = Field(default="", max_length=512)
    rpc_host: str | None = None
    rpc_port: int | None = Field(default=None, ge=1, le=65535)
    openai_base_url: str | None = Field(
        default=None,
        description="If set, this worker hosts the ingress OpenAI-compatible server (llama-server).",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerRecord(WorkerRegisterRequest):
    last_seen: datetime = Field(default_factory=utc_now)
    healthy: bool = True


class ShardStage(BaseModel):
    stage_index: int = Field(ge=0)
    worker_id: str
    role: str = Field(default="pipeline_stage")


class ModelGraphUpsert(BaseModel):
    logical_model_id: str = Field(..., min_length=1)
    runtime: str = Field(default="llama.cpp-rpc")
    ingress_worker_id: str = Field(
        ...,
        description="Worker id whose openai_base_url receives client traffic from the gateway.",
    )
    stages: list[ShardStage] = Field(default_factory=list)
    status: GraphStatus = GraphStatus.draft
    notes: str | None = None


class ModelGraph(ModelGraphUpsert):
    ingress_base_url: str | None = None
    updated_at: datetime = Field(default_factory=utc_now)


class SessionCreateResponse(BaseModel):
    session_id: str
    logical_model_id: str
    ingress_base_url: str
    stage_count: int


class OpenAIModelCard(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "zdistribute-llm-on-intel"


class OpenAIModelList(BaseModel):
    object: str = "list"
    data: list[OpenAIModelCard]


class WorkerStatusUpdate(BaseModel):
    phase: WorkerPhase
    status_message: str = Field(default="", max_length=512)


class ScheduledJobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    interval_minutes: int = Field(default=60, ge=5, le=10080)
    action: str = Field(default="cluster_health", max_length=64)
    enabled: bool = True


class ScheduledJob(ScheduledJobCreate):
    id: str
    last_run: datetime | None = None
    next_run: datetime | None = None
    last_result: str = ""


class ClusterInfo(BaseModel):
    public_coordinator_url: str
    public_gateway_url: str
    enroll_token_hint: str
    worker_count: int
    healthy_workers: int
    platform_note: str
