# Research findings — Intel Endpoint LLM Fabric

Synthesis of literature and systems review that grounds **ZDistributeLLMonIntel**. This is the technical narrative behind [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`ROADMAP.md`](ROADMAP.md).

## Executive conclusion (literature)

The “distributed LLM on Intel PCs” idea hides **three distinct problems** (model-distributed, workload-distributed, collaborative). Industry and academic systems often blend them.

## Product focus for **this repository**

**ZDistributeLLMonIntel** is **not** primarily workload-distributed (a **complete** small LLM on every PC for concurrency). It is **edge-first model-distributed inference**: **one large LLM** partitioned across many Intel devices that **cannot** load the full model alone, with **minimum cloud dependency**. See [`MISSION.md`](MISSION.md).

Engineering notes from literature still apply:

- **Cross-device sharding** is essential when memory per node is insufficient (MDI-LLM, Petals, EdgeShard, Parallax).
- **WAN layer hops** hurt inter-token latency — use admission control and site-dense sub-pipelines ([`DEPLOYMENT-PROFILES.md`](DEPLOYMENT-PROFILES.md)).
- **Collaborative** patterns (draft/verify, RAG) may **accelerate** a sharded large model but do not replace partitioning.

| Problem | What it is | Fleet effect |
|---------|------------|--------------|
| **Model-distributed inference** | One large model split across PCs; layers/experts pass activations or KV | One request can exceed single-device memory |
| **Workload-distributed inference** | Each endpoint runs a **complete** smaller model; scheduler routes prompts | Higher aggregate concurrency; one request cannot exceed one device’s model size |
| **Collaborative / hierarchical inference** | Draft/RAG/routing helpers around a **sharded** large model | Optional accelerators in this repo — not a fleet of full SLMs as the main product |

**One-sentence product position (this repo):** An open, secure **Intel Endpoint LLM Fabric** that runs **one logical large model** across many edge endpoints by **sharding**, preserves OpenAI-style client interfaces, and minimizes cloud use — with benchmarks and admission control so bad shard graphs are not deployed.

## Design principle: admission control

From network characterization work: **more devices ≠ better performance**. A node joins a generation path only when measured **compute contribution exceeds** communication, synchronization, and failure-recovery cost. The scheduler needs **benchmark-driven admission control**, not opportunistic use of every PC.

## Reference systems and papers

### Directly aligned

| System / paper | Relevance | Links |
|----------------|-----------|--------|
| **MDI-LLM** — model-distributed inference at the edge | Closest recent foundation: partition LLM across edge nodes, activation exchange, recurrent pipeline parallelism | Search: *Model-Distributed Inference for Large Language Models at the Edge* |
| **Petals** | Internet-scale collaborative inference; block chains; BLOOM-176B demo; join/leave and load balancing | [Paper](https://arxiv.org/abs/2207.07306) · [NeurIPS follow-up](https://proceedings.neurips.cc/) · [GitHub](https://github.com/bigscience-workshop/petals) |
| **EdgeShard** | Shard placement as resource/latency optimization, edge + cloud | Search: EdgeShard collaborative edge LLM |
| **Parallax** | Heterogeneous decentralized HW; pipeline + KV + batching; Qwen2.5-72B class | Review project paper / repo for current URL |
| **Distributed LLM inference on edge devices (2025)** | LAN-scale evidence (e.g. multi-phone / edge nodes) | [ACM DL](https://dl.acm.org/) — verify exact proceedings entry in bib |

**Petals caution:** Public swarms process data on others’ machines; **encryption ≠ privacy** against workers that legitimately receive activations. Sensitive workloads belong in a **private, attested trust domain** ([`SECURITY.md`](SECURITY.md)).

### Cautionary / design

| Paper | Lesson |
|-------|--------|
| **LLMs on Edge: network traffic under the loupe** | Multi-node can **degrade**; complex traffic; motivates admission control |
| **EASTER** | Robust splits under failure; redundant shard placement |
| **Dynamic split computing** | Optimal split depends on channel state → maps to dynamic choice among local SLM, prefill/decode split, speculative verify, full pipeline, RAG local + remote gen, cloud fallback |

## Intel-specific differentiation

- **Installed base** — PCs, POS, kiosks, workstations, store servers as existing substrate.
- **Heterogeneous compute** — CPU, iGPU, NPU, Arc in different roles (cf. edge pipelines: Whisper on NPU, LLM on GPU, API on CPU).
- **OpenVINO / OVMS** — Credible runtime and **OpenAI-compatible** northbound API for agent frameworks.
- **Reuse datacenter ideas carefully** — Prefill/decode disaggregation and remote KV tiers (e.g. llm-d concepts) may **not** transfer when KV-transfer overhead dominates on consumer LANs; benchmark before adopting.

## Proprietary models (product constraint)

The fabric **cannot** redistribute or decompose weights of closed models (hosted Gemini, most Copilot backends) unless the provider exposes weights or delegated execution.

**Connector model:**

- Cursor and compatible clients → configurable **OpenAI-compatible base URL** → fabric serves **approved open-weight** models (e.g. [`REFERENCE-MODEL.md`](REFERENCE-MODEL.md)).
- Gemini, Copilot, etc. remain **selectable upstream providers** via policy routing.
- **MCP** exposes local tools/data to whichever **authorized** model is selected—it is **not** the sharding protocol.

See [`INTEGRATIONS.md`](INTEGRATIONS.md).

## Related internal direction (context)

Documentation elsewhere in Intel edge/OpenVINO strategy emphasizes OpenAI-compatible OVMS for agentic frameworks and preserving LangGraph, LlamaIndex, Semantic Kernel, Haystack, and OpenAI-style client logic on-premises—this repo implements the **multi-endpoint fabric** layer above those runtimes.

## Document map

| Topic | Doc |
|-------|-----|
| Execution modes, gateway, protocol | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Phased delivery | [`ROADMAP.md`](ROADMAP.md) |
| Metrics | [`BENCHMARKS.md`](BENCHMARKS.md) |
| LAN vs WAN roles | [`DEPLOYMENT-PROFILES.md`](DEPLOYMENT-PROFILES.md) |
