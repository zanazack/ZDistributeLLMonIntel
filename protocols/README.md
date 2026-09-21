# Protocols

**ZDLI** (Z Distributed LLM on Intel) — wire formats between coordinator and workers.

## Layers

1. **Enrollment & control** — gRPC/HTTP JSON: register worker, push shard map, health.
2. **Inference data** — framed messages: forward pass tensors, metadata, stream tokens.
3. **Client gateway** — OpenAI-compatible REST (see `openapi/`).

Versioning: `zdl/v1/` prefix on HTTP paths; protobuf package `zdl.v1` when schemas land.
