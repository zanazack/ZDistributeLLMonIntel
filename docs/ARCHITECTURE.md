# Architecture — Intel Endpoint LLM Fabric

**ZDistributeLLMonIntel** runs **one large LLM** across many **Intel edge** workers by **model partitioning**. Northbound: familiar APIs. Southbound: **shards + ZDLI/EIFP**.

Mission: [`MISSION.md`](MISSION.md). Decisions: [`DECISIONS.md`](DECISIONS.md). Research: [`FINDINGS.md`](FINDINGS.md).

## Primary vs adjacent problems

| Class | Description | This repo |
|-------|-------------|-----------|
| **Model-distributed** | Split **one** LLM; each device runs **part** of the graph; activations/KV cross the wire | **Core — 100% focus** |
| **Collaborative / hierarchical** | Draft, verify, RAG, routing helpers | **Optional accelerators** on-edge only |
| **Workload-distributed** | **Full** small model per endpoint; scheduler picks a machine | **Out of primary scope** — does not increase per-request model size |

## Design principles

1. **One logical model, many physical shards** — Clients request `intel-distributed-qwen2.5-32b-instruct-q4`; coordinator assembles a **pipeline/tensor/expert graph** no single node could run alone.
2. **Edge-first, least cloud** — Steady state on Intel fleet; cloud fallback **break-glass** only ([`INTEGRATIONS.md`](INTEGRATIONS.md)).
3. **Client compatibility** — OpenAI-compatible gateway; Cursor + APIM golden paths.
4. **Admission control** — Add shard hops (especially WAN) only if ITL/TTFT still meets SLA ([`BENCHMARKS.md`](BENCHMARKS.md)).
5. **Measured placement** — Signed capability manifests (RAM, BW, RTT, ISA, runtime).
6. **MCP ≠ data plane** — MCP for tools/context; **ZDLI** moves activations and KV.

## Northbound stack

```
Cursor / agent / OpenAI-compatible client
        |
OpenAI-compatible API (one model id = one sharded run)
        |
Intel Endpoint LLM Gateway
        |
Coordinator  (shard registry, route, leases, recovery)
        |
ZDLI / EIFP  (mTLS; QUIC/gRPC data plane)
        |
Workers: shard 0 → shard 1 → … → shard N
        (llama.cpp RPC, OpenVINO/OVMS, …)
```

## Southbound: capability manifest

Workers advertise what **shard** they can host:

- Available RAM/VRAM for **weight shard** + KV budget
- CPU ISA, GPU/NPU ops, precisions, runtime id
- Network RTT/jitter/throughput to peers (critical for multi-hop graphs)
- Cached shard ids; thermal/power; trust/attestation status

Scheduler places **contiguous blocks** (pipeline), **tensor groups** (LAN), or **experts** (MoE) so the **sum of memory** across the path ≥ model requirement.

## Execution modes (core first)

| Mode | Name | Role |
|------|------|------|
| **A** | **Pipeline sharding** | **Default v1** — transformer blocks on different devices (MDI-LLM / Petals / llama.cpp RPC style) |
| **B** | **Tensor / expert parallel** | High-bandwidth LAN; MoE or TP when sync cost acceptable |
| **C** | **Speculative distributed decode** | Optional — small **draft** on one edge node, **verifier shards** on fabric (still one logical large model) |
| **D** | **Disaggregated prefill/decode** | When benchmarks show KV transfer wins on **this** LAN |

**Not primary:** “Mode 1 independent replicas” of full small LLMs across the fleet — use only for **lab smoke**, embeddings, or draft helpers tied to modes A–C.

## Partitioning model into “tasks”

Conceptually each **forward step** of a request becomes a **task chain**:

1. **Load** — ensure shard weights resident (may overlap with prior session).
2. **Compute** — matmul/attn on local shard; produce activations.
3. **Transfer** — send activation (optionally compressed) to next shard hop.
4. **Decode stream** — final shard emits tokens to gateway.

Coordinator tracks **task graph** per session; workers never see the full weights.

## Parallelism detail

| Strategy | Edge use |
|----------|----------|
| Pipeline parallel | **First target** — 2–8 Intel nodes, **Qwen2.5-32B** Q4 GGUF or OpenVINO stages |
| Tensor parallel | Same LAN, low RTT |
| Expert parallel | MoE models when adopted |

**LAN lab:** primary proving ground for modes A–B.

**WAN mesh:** **same model-distributed goal** — shards may live in **different sites** if admission control accepts RTT; prefer **fewer cross-WAN hops**, activation compression, and **site-dense** sub-pipelines ([`DEPLOYMENT-PROFILES.md`](DEPLOYMENT-PROFILES.md)).

## Protocol stack (ZDLI / EIFP)

### Control plane

Enrollment, shard registry, graph publish, health, placement, routes, failure rerouting, policy, metering.

Transports: gRPC/mTLS; HTTP/3 where allowed.

### Data plane

Activations, KV segments, speculative batches, cancel, heartbeat, idempotent request ids.

Transports: QUIC preferred for multiplexed streams; LAN may use TCP; co-located shards use shared memory / oneAPI IPC.

## Worker runtimes

| Runtime | Sharding |
|---------|----------|
| **llama.cpp RPC** | Multi-node GGUF split — **primary Phase 1 path** |
| **OpenVINO / OVMS** | IR stages per device |
| **Extensible** | Manifest-driven plugins |

Homogeneous runtime per graph in early releases.

## Reference flow — sharded chat (streaming)

1. Client → Gateway: `POST /v1/chat/completions`, model = reference logical id.
2. Gateway → Coordinator: create session on **shard graph** for that model.
3. Prompt tokens enter **shard 0**; activations flow **0→…→k**; KV stays on workers per policy.
4. Shard **k** streams tokens → Gateway → client SSE.
5. On worker loss: coordinator **reroutes** using redundant shard policy (Phase 2+, EASTER-inspired).

## Model publish

Signed manifest: per-shard hashes, stage boundaries, runtime, min cluster RAM sum.

## Trust & models

Optional attestation; default mTLS. Open-weight on fabric only — [`INTEGRATIONS.md`](INTEGRATIONS.md).

Reference weights: [`REFERENCE-MODEL.md`](REFERENCE-MODEL.md).
