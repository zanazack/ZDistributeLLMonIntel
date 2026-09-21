# Roadmap

Phased delivery for **ZDistributeLLMonIntel**. Dates TBD; reorder with product priorities.

## Phase 0 — Design (current)

- [x] Repository scaffold and architecture docs
- [ ] Confirm v1 model size and deployment target (LAN lab vs WAN)
- [ ] Choose primary worker runtime (llama.cpp vs OpenVINO vs dual)
- [ ] ZDLI control/data message schema v0.1

## Phase 1 — Lab MVP

- [ ] Coordinator service: enrollment, health, single logical model
- [ ] 2-worker pipeline parallel proof on Intel CPUs
- [ ] OpenAI-compatible connector with streaming
- [ ] End-to-end demo with one IDE (target: Cursor custom base URL)
- [ ] Docker Compose or bare-metal scripts for Intel lab

## Phase 2 — Production hardening

- [ ] mTLS everywhere, key rotation
- [ ] Quotas, tenancy, structured audit logs
- [ ] Scheduler: latency + memory-aware placement
- [ ] Model publish pipeline (signed manifests)
- [ ] Proxy-aware deployment guide (Intel corporate proxy)

## Phase 3 — Scale-out and Intel optimization

- [ ] Tensor parallel option on high-bandwidth LAN
- [ ] OpenVINO / NPU / Arc capability scheduling
- [ ] KV cache offload policy
- [ ] Disaggregated prefill/decode pools

## Phase 4 — Ecosystem connectors

- [ ] MCP server connector
- [ ] Azure APIM / Azure OpenAI-compatible policy templates
- [ ] Gemini hybrid routing documentation + reference (where permitted)
- [ ] Windows service connector for always-on home/work PCs

## Success metrics

- **Latency:** P95 time-to-first-token vs single-node baseline on same hardware sum
- **Cost:** Estimated $/1M tokens vs cloud list price for equivalent model class
- **Utilization:** Average CPU/GPU use across enrolled workers during business hours
- **Adoption:** Number of client sessions via connector vs direct cloud fallback
