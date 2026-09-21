# Architecture — Intel Endpoint LLM Fabric

**ZDistributeLLMonIntel** implements an **Intel Endpoint LLM Fabric**: northbound compatibility for existing AI tools, southbound workers on Intel endpoints, and a purpose-built **ZDLI / Endpoint Inference Fabric Protocol (EIFP)** for control and (when needed) activation transport.

Research basis: [`FINDINGS.md`](FINDINGS.md). Locked product choices: [`DECISIONS.md`](DECISIONS.md).

## Three problems (one fabric)

| # | Name | Default use |
|---|------|-------------|
| 1 | **Collaborative / hierarchical** | **Default** — SLM routing, RAG, drafts, easy vs hard policy |
| 2 | **Workload-distributed** | Full small/medium models per endpoint; scale **concurrency** across fleet |
| 3 | **Model-distributed** | Split **one** large model (e.g. Qwen2.5-32B) — **LAN clusters only** unless admission control accepts WAN hops |

**Hybrid rule:** WAN mesh emphasizes modes **1–2** (replicas + routing across sites). Mode **3** (pipeline / tensor / expert parallel) targets **latency-bounded LAN** (2–8 nodes) first.

## Design principles

1. **Client compatibility first** — OpenAI-compatible chat, embeddings, reranking, model list; provider adapters where needed; optional localhost desktop proxy ([`INTEGRATIONS.md`](INTEGRATIONS.md)).
2. **Useful product before hardest science** — Ship gateway, OVMS/OpenVINO/llama.cpp workers, replicas, semantic routing, cloud fallback **before** optimizing public federated swarms ([`ROADMAP.md`](ROADMAP.md)).
3. **Admission control** — Add a node to a hot path only if benchmarks show net win on ITL/TTFT vs bytes and recovery cost ([`BENCHMARKS.md`](BENCHMARKS.md)).
4. **Fail closed on security** — Private trust domain for sensitive inference; mTLS baseline; optional attestation ([`SECURITY.md`](SECURITY.md)).
5. **Measured placement** — Schedules from **signed capability manifests** and live telemetry, not TOPS labels alone.
6. **MCP is not the data plane** — MCP for tools, retrieval, enterprise context; **not** for activations or distributed KV sync.

## Northbound stack

```
Cursor / agent framework / OpenAI-compatible client
        |
OpenAI-compatible inference API  (/v1/chat/completions, models, embeddings, …)
        |
Intel Endpoint LLM Gateway  (connectors/openai-gateway + enterprise APIM)
   /    |    \
Local   Distributed   Approved cloud
replica fabric         fallback
pool    (LAN modes 2–4)
        |
Encrypted fabric protocol (ZDLI / EIFP)
        |
Intel endpoint workers  (llama.cpp, OpenVINO/OVMS, …)
```

## Southbound: capability manifest

Each worker publishes a **signed** manifest (illustrative fields):

- CPU model and ISA (AMX, AVX-512, …)
- System RAM and **available** RAM
- GPU type and VRAM; NPU generation and supported ops
- Supported precisions and runtimes (`llama.cpp-rpc`, `openvino`, `ovms`, …)
- Measured memory bandwidth; thermal/power policy
- Network RTT, jitter, throughput, loss (to coordinator/peers)
- Cached model shards; KV-cache capacity
- Attestation/trust status; load; expected availability window

The scheduler builds an **execution graph** from measurements plus policy—not static homogeneity assumptions.

## Five execution modes

| Mode | Name | When |
|------|------|------|
| **1** | **Independent replicas** | Each endpoint runs a complete ~1B–8B (or fit-sized) model; route for concurrency — simplest fleet win |
| **2** | **Pipeline sharding** | Contiguous blocks on different devices (Petals / MDI-LLM style); no single device holds full **≥16B** reference |
| **3** | **Tensor / expert parallel** | Tight LAN only; high sync frequency |
| **4** | **Speculative distributed decoding** | Local draft model; distributed or LAN verifier batch (EAGLE-style paths on Intel CPU/GPU/NPU) |
| **5** | **Semantic / policy routing** | Easy → SLM on idle endpoint; hard → LAN cluster **Qwen2.5-32B** fabric or approved cloud |

Dynamic split (from dynamic split computing literature) chooses among: local-only SLM; local prefill + remote decode; draft + verify; full pipeline; RAG local + gen remote; cloud fallback.

## Roles

### Gateway (connector)

- Terminates client TLS; OpenAI-compatible surface.
- Tenant policy, metering, **cloud fallback**.
- Does **not** require clients to understand sharding.

### Coordinator (control plane)

- Enrollment, identity, capability discovery, model/shard registry.
- Health, thermal, load, **placement**, route creation, lease renewal, failure recovery.
- **Managed coordinator** for enterprise; optional DHT-style discovery for decentralized labs (later).
- Admission control gates for mode 3 paths.

### Worker

- Runs full model (mode 1) or shard (modes 2–3) or draft/verify role (mode 4).
- Sandboxed; no arbitrary client code; signed graph updates only.

## Parallelism (mode 2–3 detail)

| Strategy | When | Tradeoff |
|----------|------|----------|
| Pipeline parallel | LAN, memory-bound **≥10B** | Pipeline bubbles; lower sync than TP |
| Tensor parallel | LAN, low RTT, high bisection BW | Frequent all-reduce |
| Expert parallel (MoE) | MoE models | Load imbalance |
| Prefill/decode disaggregation | Measured net benefit only | KV transfer may dominate on PC LANs |

**Reference LAN target:** 2–8 Intel systems, **Qwen2.5-32B-Instruct**, Q4 GGUF or OpenVINO export ([`REFERENCE-MODEL.md`](REFERENCE-MODEL.md)).

**WAN default:** TLS-only mesh ([`DEPLOYMENT-PROFILES.md`](DEPLOYMENT-PROFILES.md)) for **replicas + policy routing**; cross-site **pipeline** only with explicit SLA + compression and expected ITL tradeoffs.

## Protocol stack (ZDLI / EIFP)

### Control plane

Enrollment, capability discovery, shard registry, health/thermal, placement, routes, leases, failure recovery, policy, usage accounting.

**Transports:** gRPC over mTLS (proxy-friendly); HTTP/3 where UDP allowed; optional DHT discovery (Phase 3).

### Data plane (modes 2–4)

Prototype candidates:

- **QUIC** — encrypted multiplexed streams, migration, reduced HOL blocking
- **gRPC** over HTTP/2 or HTTP/3 for RPC control
- **Same-machine** — shared memory, oneAPI IPC
- **Workstation clusters** — optional RDMA-class transport
- **Activation compression / quantization** before WAN or slow hops
- **Priority streams** — token-path activations vs shard load / telemetry

Message types: activation tensors, KV segments, speculative token batches, routing metadata, cancellation, heartbeat, replay-safe request IDs.

## Worker runtime backends

| Runtime | Artifacts | Typical mode |
|---------|-----------|--------------|
| **OpenVINO / OVMS** | IR, OpenAI-compatible server | 1, 5; enterprise northbound |
| **llama.cpp RPC** | GGUF | 1–2, 4 on CPU/AMX |
| **IPEX / future** | PyTorch, vLLM-CPU, … | Extensible via manifest |

Homogeneous runtime per pipeline in early Phase 2; heterogeneous stages remain research.

## Reference flows

### Chat (mode 5 → mode 1 replica)

1. Client → Gateway → Coordinator classifies difficulty.
2. Route to local SLM replica or queue for larger model.
3. Stream tokens; log cloud-fallback decision if policy triggers.

### Chat (mode 2 LAN, reference 32B)

1. Client → Gateway → Coordinator admission-checks pipeline `W0→…→Wk`.
2. Activations over LAN data plane; KV affinity on workers.
3. Final stage streams to gateway.

### Model publish

Signed manifest, per-shard hashes, push to workers, ready state.

## Trust and models (locked)

- Attestation **optional**; default PKI + mTLS.
- WAN **TLS-only**; VPN **optional**.
- Open-weight catalog only on fabric; proprietary APIs as **upstream** ([`INTEGRATIONS.md`](INTEGRATIONS.md)).

## Related code / papers

See comparison table in [`FINDINGS.md`](FINDINGS.md). This repo is **not** a fork of Petals or OVMS; it composes them as worker backends where appropriate.
