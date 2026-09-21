# ZDistributeLLMonIntel

**Intel Endpoint LLM Fabric** — open, secure distributed inference across Intel PCs and edge systems, with **pluggable connectors** so tools like Cursor and enterprise APIM keep using OpenAI-style APIs.

Public OSS: [github.com/zanazack/ZDistributeLLMonIntel](https://github.com/zanazack/ZDistributeLLMonIntel) (Apache 2.0).

## Executive summary

Three different problems sit behind “run LLMs on many Intel machines”:

1. **Collaborative / hierarchical** — route easy work to small local models; hard work to larger LAN clusters or approved cloud (**default**).
2. **Workload-distributed** — full models on many endpoints; scale **concurrency** (one request still bounded by one device’s model size).
3. **Model-distributed** — split **one** large model across nodes (activations/KV); use inside **latency-bounded LANs** when admission control proves a net win—not by default over WAN.

**Recommendation:** Hybrid of all three; ship a **useful gateway + replicas + routing first**, add **LAN pipeline sharding** for models like **Qwen2.5-32B** in Phase 2. See [`docs/FINDINGS.md`](docs/FINDINGS.md).

## Vision

| Goal | Approach |
|------|----------|
| Use Intel install base efficiently | Modes 1–5 + measured capability manifests ([`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)) |
| Plug into existing AI tools | OpenAI-compatible **gateway**; Cursor + APIM first |
| Lower cloud cost & dependency | Local replicas, semantic routing, selective LAN composition |
| Trust | mTLS baseline; optional attestation; **private domain** for sensitive sharded inference |

## v1 scope (locked)

| Area | Choice |
|------|--------|
| Strategy | **Hybrid**; collaborative default; LAN sharding Phase 2 |
| Deployment | **LAN lab** (pipeline) + **WAN mesh** (replicas/routing, TLS-only) |
| Models | **≥10B**; reference **[Qwen2.5-32B-Instruct](docs/REFERENCE-MODEL.md)** |
| Workers | **llama.cpp RPC**, **OpenVINO/OVMS**, extensible |
| Clients | **Cursor** + **Azure APIM** |
| WAN | **TLS-only**; VPN **optional** |

Details: [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Architecture (northbound)

```
Cursor / agent / OpenAI-compatible client
        → Intel Endpoint LLM Gateway (connectors)
        → Coordinator (placement, policy, admission control)
        → Workers (replica | shard | draft/verify)
        ZDLI / EIFP encrypted fabric
```

MCP = tools/context only; not the sharding wire protocol.

## Repository layout

| Path | Purpose |
|------|---------|
| [`docs/FINDINGS.md`](docs/FINDINGS.md) | Papers, systems, product positioning |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Five modes, protocol, manifests |
| [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) | TTFT, ITL, bytes/token, admission tests |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Phase 1 product → Phase 2 LAN shard → federation |
| [`connectors/`](connectors/) | openai-gateway, enterprise-apim |
| [`protocols/`](protocols/) | ZDLI / EIFP sketches |

## Status

**Design aligned with research findings.** Phase 1 implementation: gateway, OVMS/llama replicas, capability discovery, semantic routing, cloud fallback, Cursor + APIM.

## Getting started

1. [`docs/FINDINGS.md`](docs/FINDINGS.md) — why three problems and admission control matter  
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — execution modes and protocol  
3. [`docs/ROADMAP.md`](docs/ROADMAP.md) — what to build first  

## License

Apache License 2.0 — [LICENSE](LICENSE). Contributing: [CONTRIBUTING.md](CONTRIBUTING.md).
