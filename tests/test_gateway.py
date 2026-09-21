from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from zdli.gateway.app import create_app

AUTH = {"Authorization": "Bearer dev-gateway-key"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_models_list(client: TestClient) -> None:
    with patch("zdli.gateway.app._fetch_graphs", new=AsyncMock(return_value=[])):
        r = client.get("/v1/models", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["object"] == "list"
    assert len(r.json()["data"]) >= 1


def test_chat_requires_model(client: TestClient) -> None:
    r = client.post("/v1/chat/completions", json={"messages": []}, headers=AUTH)
    assert r.status_code == 400
