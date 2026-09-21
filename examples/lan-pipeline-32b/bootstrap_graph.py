#!/usr/bin/env python3
"""Register the reference 2-stage pipeline graph with the coordinator."""

from __future__ import annotations

import argparse
import sys

import httpx

from zdli.schemas import REFERENCE_LOGICAL_MODEL, GraphStatus, ModelGraphUpsert, ShardStage


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Qwen2.5-32B sharded graph")
    parser.add_argument("--coordinator", default="http://127.0.0.1:7443")
    parser.add_argument("--token", default="dev-coordinator-token")
    parser.add_argument("--shard0", default="shard-0")
    parser.add_argument("--ingress", default="shard-1")
    args = parser.parse_args()

    graph = ModelGraphUpsert(
        logical_model_id=REFERENCE_LOGICAL_MODEL,
        runtime="llama.cpp-rpc",
        ingress_worker_id=args.ingress,
        stages=[
            ShardStage(stage_index=0, worker_id=args.shard0),
            ShardStage(stage_index=1, worker_id=args.ingress),
        ],
        status=GraphStatus.ready,
        notes="LAN pipeline MVP — llama-server on ingress with RPC to shard-0",
    )
    url = f"{args.coordinator.rstrip('/')}/zdl/v1/graphs/{REFERENCE_LOGICAL_MODEL}"
    headers = {"Authorization": f"Bearer {args.token}"}
    with httpx.Client(timeout=30.0) as client:
        resp = client.put(url, json=graph.model_dump(), headers=headers)
    if resp.status_code >= 400:
        print(resp.text, file=sys.stderr)
        return 1
    print(resp.json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
