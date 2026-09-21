# Roadmap

**North star:** **one large LLM sharded across Intel edge devices** — [`MISSION.md`](MISSION.md). Not a fleet-of-full-small-models product.

## Phase 0 — Design

- [x] Mission, architecture, decisions
- [x] Reference **Qwen2.5-32B-Instruct**
- [x] ZDLI control plane v0.1 (HTTP API + OpenAPI stub)
- [x] Python coordinator, gateway, worker agent (in-memory MVP)
- [ ] Shard manifest v0.1 (signed hashes per stage)
- [ ] Data plane (activations over QUIC)

## Phase 1 — Sharded inference MVP (edge, minimal cloud)

**Fabric (core)**

- [x] Coordinator: enrollment, **shard graph**, session → ingress URL
- [ ] **Pipeline sharding** — llama.cpp RPC lab proof, **≥2 workers**, **Qwen2.5-32B** no full copy on any one node
- [ ] OpenVINO worker: at least one **stage** of same logical model
- [ ] Signed capability manifests (RAM, RTT, runtime)
- [ ] LAN lab demo: end-to-end sharded generation

**Gateway & connectors**

- [x] `connectors/openai-gateway/` — `zdli.gateway` proxies to sharded ingress
- [ ] `connectors/enterprise-apim/` — enterprise ingress to same gateway
- [ ] Cursor + APIM E2E on **sharded** reference model
- [ ] Cloud fallback **optional**, off by default in lab configs

**WAN (same model, many sites)**

- [ ] Multi-site workers enrolled over **TLS-only** mesh
- [ ] Shard placement with **admission control** (reject graphs that fail ITL SLA)
- [ ] Activation compression on slow links (initial prototype)

**Ops**

- [ ] Windows + Linux workers; Intel proxy guide; lab compose/scripts

## Phase 2 — Efficiency & resilience on edge

- [ ] Topology-aware shard placement (BW, ISA, GPU/NPU)
- [ ] QUIC data plane; redundant shard replicas; failure rerouting
- [ ] KV affinity; continuous batching across stages where safe
- [ ] Speculative decode (draft helper + sharded verifier) — still one logical 32B
- [ ] Full [`BENCHMARKS.md`](BENCHMARKS.md) harness + admission automation

## Phase 3 — Hardening

- [ ] mTLS rotation, tenancy, audit (APIM alignment)
- [ ] Tensor/expert parallel on qualifying LANs
- [ ] Optional attestation packs

## Phase 4 — Ecosystem

- [ ] MCP for tools (not sharding wire)
- [ ] Federation research (intermittent nodes) — after LAN/WAN sharding proven
- [ ] Additional worker backends

## Success metrics

- **Functional:** 32B-class model completes on cluster where **each node fails alone**
- **Edge:** % tokens generated without cloud
- **Latency:** TTFT / ITL p95 on LAN vs WAN shard graphs
- **Efficiency:** bytes activation per token; joules per token
