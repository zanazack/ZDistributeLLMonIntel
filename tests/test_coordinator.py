import pytest
from fastapi.testclient import TestClient

from zdli.coordinator.app import create_app
from zdli.schemas import (
    REFERENCE_LOGICAL_MODEL,
    GraphStatus,
    ModelGraphUpsert,
    ShardStage,
    WorkerRegisterRequest,
)
from zdli.store import CoordinatorStore

AUTH = {"Authorization": "Bearer dev-coordinator-token"}
AUTH_ENROLL = {"Authorization": "Bearer dev-enroll-token"}


@pytest.fixture
def client() -> TestClient:
    store = CoordinatorStore()
    return TestClient(create_app(store))


def _register(client: TestClient, worker_id: str, openai: str | None = None) -> None:
    body = WorkerRegisterRequest(
        worker_id=worker_id,
        site_id="lab",
        openai_base_url=openai,
        ram_available_mb=32768,
    )
    r = client.post("/zdl/v1/workers/register", json=body.model_dump(), headers=AUTH)
    assert r.status_code == 200


def test_register_and_graph(client: TestClient) -> None:
    _register(client, "shard-0", None)
    _register(client, "shard-1", "http://127.0.0.1:8081")
    graph = ModelGraphUpsert(
        logical_model_id=REFERENCE_LOGICAL_MODEL,
        ingress_worker_id="shard-1",
        stages=[
            ShardStage(stage_index=0, worker_id="shard-0"),
            ShardStage(stage_index=1, worker_id="shard-1"),
        ],
        status=GraphStatus.ready,
    )
    r = client.put(
        f"/zdl/v1/graphs/{REFERENCE_LOGICAL_MODEL}",
        json=graph.model_dump(),
        headers=AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ingress_base_url"] == "http://127.0.0.1:8081"
    assert len(data["stages"]) == 2


def test_session_requires_ingress(client: TestClient) -> None:
    _register(client, "shard-0", None)
    graph = ModelGraphUpsert(
        logical_model_id=REFERENCE_LOGICAL_MODEL,
        ingress_worker_id="shard-0",
        stages=[ShardStage(stage_index=0, worker_id="shard-0")],
        status=GraphStatus.ready,
    )
    client.put(
        f"/zdl/v1/graphs/{REFERENCE_LOGICAL_MODEL}",
        json=graph.model_dump(),
        headers=AUTH,
    )
    r = client.post(
        "/zdl/v1/sessions",
        params={"logical_model_id": REFERENCE_LOGICAL_MODEL},
        headers=AUTH,
    )
    assert r.status_code == 503


def test_register_with_enroll_token(client: TestClient) -> None:
    body = WorkerRegisterRequest(worker_id="edge-1", site_id="wan")
    r = client.post("/zdl/v1/workers/register", json=body.model_dump(), headers=AUTH_ENROLL)
    assert r.status_code == 200


def test_session_ok(client: TestClient) -> None:
    _register(client, "ingress", "http://llama.local:8081")
    graph = ModelGraphUpsert(
        logical_model_id=REFERENCE_LOGICAL_MODEL,
        ingress_worker_id="ingress",
        stages=[ShardStage(stage_index=0, worker_id="ingress")],
        status=GraphStatus.ready,
    )
    client.put(
        f"/zdl/v1/graphs/{REFERENCE_LOGICAL_MODEL}",
        json=graph.model_dump(),
        headers=AUTH,
    )
    r = client.post(
        "/zdl/v1/sessions",
        params={"logical_model_id": REFERENCE_LOGICAL_MODEL},
        headers=AUTH,
    )
    assert r.status_code == 200
    assert r.json()["ingress_base_url"] == "http://llama.local:8081"
