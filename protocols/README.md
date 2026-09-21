# Protocols — ZDLI / Endpoint Inference Fabric Protocol (EIFP)

Purpose-built **southbound** protocol between coordinator and Intel workers. **Not** MCP and not the OpenAI client API.

## Layers

1. **Control plane** — enrollment, signed capability manifests, model/shard registry, health/thermal, placement, routes, leases, failure recovery, policy, metering.
2. **Data plane** — activations, KV segments, speculative batches, cancellation, heartbeats, replay-safe request IDs (modes 2–4).

## Transports (prototype order)

| Transport | Use |
|-----------|-----|
| gRPC over mTLS | Control; corporate HTTP proxy friendly |
| QUIC | Multiplexed data plane; migration; reduced HOL blocking |
| HTTP/3 | Where UDP allowed |
| Shared memory / oneAPI IPC | Co-located workers on one OS |
| Optional RDMA-class | Workstation / edge-server clusters |

Features: activation compression/quantization before slow links; priority streams (token path vs shard load/telemetry).

Versioning: `zdl/v1/` HTTP prefix; future `zdl.v1` protobuf package.

Client-facing API remains OpenAI-compatible — see `openapi/coordinator-gateway.yaml`.

Design context: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md), [`docs/FINDINGS.md`](../docs/FINDINGS.md).
