# Roadmap

Aligned with [`FINDINGS.md`](FINDINGS.md): **collaborative + workload distribution first**, **LAN model sharding second**, **broad federation third**. Locked decisions: [`DECISIONS.md`](DECISIONS.md).

## Phase 0 — Design

- [x] Repository scaffold and architecture docs
- [x] Three-problem framework and five execution modes documented
- [x] LAN + WAN scope (WAN = replicas/routing default; LAN = sharding)
- [x] Reference model **Qwen2.5-32B-Instruct**
- [ ] ZDLI / EIFP control message schema v0.1
- [ ] Capability manifest schema v0.1
- [ ] Shard manifest for Phase 2 LAN demos

## Phase 1 — Useful product (ship before hardest science)

Goal: Lower cloud usage and plug into **Cursor + APIM** with minimal client changes.

**Gateway & connectors**

- [ ] `connectors/openai-gateway/` — chat, models, embeddings (OpenAI-compatible)
- [ ] `connectors/enterprise-apim/` — policies, upstream, tenant mapping
- [ ] Cloud fallback and policy routing hooks (mode 5 baseline)

**Workers & runtime**

- [ ] OpenVINO / **OVMS** worker with OpenAI-compatible northbound where applicable
- [ ] llama.cpp worker for **replica** mode (1B–8B + dev paths)
- [ ] Signed **capability discovery** and fleet telemetry
- [ ] Windows and Linux worker packages (lab)

**Intelligence**

- [ ] Semantic / policy request routing (easy → SLM replica, hard → larger local or cloud)
- [ ] Local RAG + embeddings tier (NPU/GPU/CPU per manifest)

**Ops**

- [ ] Managed coordinator MVP (enrollment, health, site labels)
- [ ] WAN: **TLS-only** multi-site **replica** pools + routing (not layer pipeline default)
- [ ] Docker Compose / lab scripts; Intel proxy guide

**Demos**

- [ ] Cursor → gateway → local replica pool
- [ ] APIM → gateway → same fabric
- [ ] Reference **Qwen2.5-32B** on **single** high-RAM node or approved cloud fallback until Phase 2 LAN shard

## Phase 2 — LAN-scale large model (controlled 2–8 nodes)

Goal: **Model-distributed** inference where admission control says it wins.

- [ ] Transformer-block pipeline sharding (llama.cpp RPC + OpenVINO paths)
- [ ] Topology-aware placement (RAM, BW, ISA, GPU/NPU)
- [ ] QUIC (or prioritized) activation transport; activation compression
- [ ] Redundant shard placement (EASTER-style recovery)
- [ ] KV-cache affinity; continuous batching
- [ ] Speculative distributed decoding (mode 4) — Intel CPU/GPU/NPU draft/verify
- [ ] Failure rerouting; benchmark harness ([`BENCHMARKS.md`](BENCHMARKS.md))
- [ ] E2E: **Qwen2.5-32B-Instruct** pipeline on LAN lab

## Phase 3 — Production hardening

- [ ] mTLS rotation, quotas, audit (APIM + coordinator)
- [ ] Benchmark-driven **admission control** in production scheduler
- [ ] Optional attestation policy packs
- [ ] Tensor/expert parallel on qualifying LANs only

## Phase 4 — Broad federated fabric (after Phase 2 proves LAN)

- [ ] Intermittent endpoints, multi-org trust, Sybil resistance
- [ ] Economic / metering models for shared capacity
- [ ] Byzantine-result detection research
- [ ] MCP connector for tools (not sharding plane)
- [ ] Gemini hybrid docs; Windows always-on service

## Success metrics

See [`BENCHMARKS.md`](BENCHMARKS.md): TTFT, ITL p95/p99, bytes/token, joules/token, cloud tokens avoided, recovery time—not aggregate TPS alone.
