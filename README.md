# ZDistributeLLMonIntel

**Run one large LLM across many Intel edge devices** — partition the model into shards and tasks so **≥10B** models execute on commodity PCs that **cannot** hold the full weights locally. **Edge-first**, **minimum cloud dependency**, **OpenAI-compatible** connectors for Cursor, APIM, and similar tools.

Public OSS: [github.com/zanazack/ZDistributeLLMonIntel](https://github.com/zanazack/ZDistributeLLMonIntel) (Apache 2.0).

## Why

A single Intel endpoint often lacks RAM and accelerator memory for **Qwen2.5-32B-class** models. The fleet **does** have aggregate memory and compute — this project **stitches endpoints into one virtual inference engine** for **one logical model per request**.

This is **not** primarily “run a small complete model on every PC for more concurrent chats.” That is workload distribution; see [`docs/MISSION.md`](docs/MISSION.md) for the distinction.

## How

| Layer | Role |
|-------|------|
| **Gateway** | OpenAI-compatible API; one model id → one sharded run |
| **Coordinator** | Shard map, placement, routes, failure recovery, admission control |
| **Workers** | **Partial model** + llama.cpp RPC / OpenVINO / other runtimes |
| **ZDLI / EIFP** | Encrypted activations, KV, control (TLS-only WAN; VPN optional) |

```
Client → Gateway → Coordinator → [Worker shard 0 → … → shard N] → tokens
```

## v1 scope (locked)

| Area | Choice |
|------|--------|
| **Goal** | **Model-distributed** inference on Intel edge |
| **Models** | **≥10B**; reference **[Qwen2.5-32B-Instruct](docs/REFERENCE-MODEL.md)** |
| **Footprint** | **LAN lab** + **WAN mesh** (shard across sites when benchmarks allow) |
| **Runtimes** | **llama.cpp RPC**, **OpenVINO/OVMS** |
| **Clients** | **Cursor** + **Azure APIM** |
| **Cloud** | **Optional fallback only** |

[`docs/DECISIONS.md`](docs/DECISIONS.md) · [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · [`docs/ROADMAP.md`](docs/ROADMAP.md)

## Status

Design + mission locked; implementation targets **sharded pipeline MVP** for reference 32B model, then WAN multi-site shards with admission control.

## Getting started

1. [`docs/MISSION.md`](docs/MISSION.md) — product focus vs workload-distributed SLM fleets  
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — sharding modes, manifests, protocol  
3. [`docs/FINDINGS.md`](docs/FINDINGS.md) — papers and engineering cautions  

## License

Apache 2.0 — [LICENSE](LICENSE). [CONTRIBUTING.md](CONTRIBUTING.md).
