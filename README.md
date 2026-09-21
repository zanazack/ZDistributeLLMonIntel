# ZDistributeLLMonIntel

**Distributed large-language-model inference across Intel-based endpoints**, with a **pluggable connector** model so existing AI clients (IDE assistants, chat UIs, automation) can route work to on-prem and edge capacity instead of defaulting to hyperscale cloud-only inference.

## Problem

Large models are sized for datacenter GPUs. Commodity PCs and workstations (Core, Xeon, Arc, integrated NPUs) are rarely used as a **coordinated pool** for a single logical model. That leaves cost, privacy, and latency on the table—and keeps GenAI tied to cloud APIs.

## Vision

| Goal | Approach |
|------|----------|
| Use many Intel machines as one inference fabric | Layer-wise or tensor-parallel sharding + a **coordinator** that presents one logical model |
| Plug into tools users already have | **OpenAI-compatible** and tool-specific **connectors** (proxy / sidecar / MCP) |
| Low latency at scale | Region-aware scheduling, streaming, binary protocols optional on the data plane |
| Trust on untrusted networks | **TLS/mTLS**, attestation hooks (optional), tenant isolation at the coordinator |
| Lower token cost & cloud dependency | Prefer local/edge completion; cloud fallback only when configured |

## Conceptual architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  AI clients (Cursor, VS Code + Copilot-style APIs, Gemini      │
│  tooling, custom apps)                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS (OpenAI-compatible / tool SDK)
┌────────────────────────────▼────────────────────────────────────┐
│  Connector layer (pluggable): auth translation, routing,        │
│  policy, metering, cloud fallback                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ ZDLI control + encrypted data plane
┌────────────────────────────▼────────────────────────────────────┐
│  Coordinator: shard map, session affinity, load balance,        │
│  KV-cache policy, health, optional Intel-specific runtimes      │
└──────────────┬──────────────────────────────┬───────────────────┘
               │ mTLS/gRPC or QUIC streams    │
     ┌─────────▼─────────┐           ┌────────▼────────┐
     │  Worker (shard 0) │  ...      │  Worker (shard N)│
     │  Intel CPU / GPU  │           │  Intel CPU / NPU │
     │  OpenVINO / IPEX  │           │  llama.cpp / …   │
     └───────────────────┘           └─────────────────┘
```

**ZDLI** (working name: *Z Distributed LLM on Intel*) is the protocol family between coordinator and workers—defined incrementally in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Repository layout

| Path | Purpose |
|------|---------|
| [`docs/`](docs/) | Architecture, security, integrations, roadmap |
| [`connectors/`](connectors/) | Client-facing adapter specs and future implementations |
| [`protocols/`](protocols/) | Wire formats, API sketches, OpenAPI stubs |
| [`examples/`](examples/) | Minimal deployment and client configuration patterns |

## Status

**Exploration / design phase.** Implementation will follow agreed priorities (coordinator MVP, worker runtime, first connector). See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Getting started (developers)

1. Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md).
2. Comment on or extend the roadmap in [`docs/ROADMAP.md`](docs/ROADMAP.md).
3. Watch this repo for coordinator/worker and connector milestones.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
