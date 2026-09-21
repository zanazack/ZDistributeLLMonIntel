# Roadmap

Phased delivery for **ZDistributeLLMonIntel**. Grounded in [`DECISIONS.md`](DECISIONS.md): **LAN + WAN**, **≥10B**, **llama.cpp + OpenVINO**, **Cursor + APIM**, **public OSS**.

## Phase 0 — Design

- [x] Repository scaffold and architecture docs
- [x] Confirm v1 scope: LAN lab **and** WAN mesh
- [x] Minimum model class: **10B+**
- [x] Worker runtimes: **llama.cpp RPC**, **OpenVINO**, extensible matrix
- [x] Golden-path clients: **Cursor OpenAI base URL** + **enterprise APIM**
- [ ] ZDLI control/data message schema v0.1
- [ ] Reference model selection (≥10B) and shard manifest format

## Phase 1 — v1 MVP (dual footprint, dual client)

**Fabric**

- [ ] Coordinator: enrollment, site labels, health, single logical **≥10B** model
- [ ] LAN lab: 2-worker pipeline proof (llama.cpp RPC on Intel CPU)
- [ ] WAN mesh: second site with site-biased scheduling + WAN link policy (lab simulation or two physical sites)
- [ ] OpenVINO worker adapter: load and run a ≥10B-class graph on at least one Intel target (CPU or GPU)

**Connectors (both golden paths)**

- [ ] `connectors/openai-gateway/` — OpenAI-compatible streaming (Cursor base URL)
- [ ] `connectors/enterprise-apim/` — Azure APIM policies + upstream to coordinator/connector
- [ ] End-to-end: Cursor → connector → LAN pipeline
- [ ] End-to-end: APIM → connector/coordinator → fabric (tenant + API key policy)

**Ops**

- [ ] Docker Compose or bare-metal scripts for Intel lab
- [ ] Proxy-aware deployment guide (Intel corporate proxy)

## Phase 2 — Production hardening

- [ ] mTLS everywhere, key rotation
- [ ] Quotas, tenancy, structured audit logs (APIM + coordinator alignment)
- [ ] Scheduler: latency, memory, **site/RTT**-aware placement
- [ ] Model publish pipeline (signed manifests, ≥10B shard verification)
- [ ] WAN activation compression options

## Phase 3 — Scale-out and Intel optimization

- [ ] Tensor parallel on high-bandwidth LAN
- [ ] OpenVINO NPU / Arc scheduling in capability matrix
- [ ] KV cache offload and site-local affinity
- [ ] Disaggregated prefill/decode pools

## Phase 4 — Ecosystem expansion

- [ ] MCP server connector
- [ ] Gemini hybrid routing documentation + reference (where permitted)
- [ ] Windows service connector for always-on endpoints
- [ ] Additional worker backends (vLLM-CPU, community plugins)

## Success metrics

- **Latency:** P95 TTFT on LAN vs WAN mesh (labeled separately); compare to single-node sum-of-RAM baseline for **≥10B**
- **Cost:** Estimated $/1M tokens vs cloud for equivalent model class
- **Utilization:** Average CPU/GPU/NPU use across enrolled workers
- **Adoption:** Sessions via **Cursor connector** vs **APIM** vs cloud fallback
