# Architecture

This document captures the **distributed LLM on Intel** design space and the direction for **ZDistributeLLMonIntel**. It is meant to evolve with your product decisions.

## Design principles

1. **Client compatibility first** — Most tools speak OpenAI-style chat/completions or can be fronted by a small proxy. Custom protocols stay on the worker fabric, not in every IDE.
2. **Fail closed on security** — Workers join only with authenticated enrollment; inference traffic is encrypted; policy is enforced at the connector and coordinator.
3. **Latency-aware placement** — Shard work to nodes that meet SLA (RTT, bandwidth, memory headroom), not round-robin only.
4. **Runtime agnostic, Intel-optimized** — Workers may use OpenVINO, Intel Extension for PyTorch, llama.cpp (AVX-512/AMX), or future oneAPI paths; the coordinator treats them as capability advertisements.
5. **Incremental complexity** — Start with pipeline parallelism (layers on different hosts), add tensor parallel and disaggregated prefill/decode when needed.

## Roles

### Connector (edge / user machine / small server)

- Terminates client TLS.
- Maps client identity (API key, OAuth, enterprise SSO) to **tenant** and **policy**.
- Exposes **OpenAI-compatible** endpoints where possible ([`INTEGRATIONS.md`](INTEGRATIONS.md)).
- Optional **cloud fallback** when local fabric is saturated or model unavailable.
- Emits usage metrics for chargeback and token-cost comparison.

### Coordinator (control plane + optional inference gateway)

- Maintains **shard graph**: which layers (or tensor shards) live on which workers.
- **Schedules** new sessions: picks worker chain minimizing critical-path latency.
- **Streams** tokens: merges partial outputs from the pipeline in order.
- **KV cache**: policy for offloading, replication, or migration (later phase).
- **Health**: heartbeats, backpressure, automatic shard exclusion.

### Worker (Intel endpoint)

- Runs a **shard runtime** (subset of model weights + ops).
- Registers **capabilities**: RAM, AVX-512/AMX, Arc GPU, NPU, max batch, supported quant formats.
- Participates in **collective** steps when using tensor parallel (NCCL/Gloo or custom over RDMA/TCP).
- Sandboxed execution: no arbitrary code from clients; only coordinator-signed graph updates.

## Parallelism strategies

| Strategy | When | Tradeoff |
|----------|------|----------|
| **Pipeline parallel** | Few powerful nodes, large model | Bubble overhead; simpler networking |
| **Tensor parallel** | Low-latency LAN, need faster per-token | All-reduce heavy; needs good bisection bandwidth |
| **Expert parallel (MoE)** | MoE models | Routing + load imbalance |
| **Disaggregated prefill/decode** | Mixed client RTT | Two pool types; better tail latency |

**Recommended MVP:** pipeline parallel over 2–8 homogeneous Intel hosts on the same site, int4/int8 weights, streaming decode from the last stage.

## Protocol stack (ZDLI — working name)

### Control plane

- **Enrollment**: worker obtains cert from coordinator (or enterprise PKI).
- **Heartbeat + metrics**: CPU/GPU util, queue depth, thermal throttling flags.
- **Graph updates**: model version, shard boundaries, rollback.

Suggested transport: **gRPC over mTLS** (mature tooling behind corporate proxies) or **HTTP/3** where UDP is allowed.

### Data plane

- **Forward activations** between stages (compressed float16/bfloat16 or quantized activations).
- **Streaming tokens** from final stage to coordinator → connector.
- Optional: **QUIC bidirectional streams** for multiplexed sessions on one connection.

Latency tactics:

- Pin sessions to a fixed pipeline (**affinity**) to reuse KV locally.
- **Micro-batching** only when SLA allows.
- **Overlap** compute and network (double buffering between stages).

## Intel-specific optimization hooks

Workers advertise and the scheduler may prefer:

- **AMX** / **AVX-512** for GEMM-heavy kernels (llama.cpp, IPEX).
- **OpenVINO** for converted IR models on CPU/GPU/NPU.
- **Arc GPU** for medium models locally before spanning nodes.
- **Core Ultra NPU** for small models or embedding/rerank tiers—not usually full 70B+ alone.

The coordinator does **not** require a single stack; it matches **model artifact format** to worker runtime via a **capability matrix**.

## Reference flows

### Chat completion (streaming)

1. Client → Connector: `POST /v1/chat/completions` (stream=true).
2. Connector → Coordinator: authenticated session create.
3. Coordinator assigns pipeline `W0 → W1 → … → Wk`.
4. Prompt tokens flow stage-wise; KV stays on workers per policy.
5. Final stage streams tokens → Coordinator → Connector → Client SSE.

### Model publish (admin)

1. Admin uploads sharded weights + manifest (hash per shard).
2. Coordinator verifies and pushes load commands to workers.
3. Workers acknowledge; graph state becomes **ready**.

## Related ecosystems (inform comparison, not dependencies)

- **llama.cpp RPC** — multi-node split; good pattern for commodity LAN.
- **Exo / similar** — peer discovery; inspiration for home/small-office meshes.
- **Petals / distributed HF** — pipeline over Internet; latency lessons for WAN.
- **OpenAI API** — de facto client contract for connectors.

## Open decisions (for your next directions)

- Target **minimum** model class for v1 (e.g. 7B vs 70B)?
- **WAN vs LAN-only** for worker membership?
- **Enterprise** (AD/SSO, audit) vs **community** mesh first?
- Mandatory **TEE/attestation** (SGX/TDX) or optional?
- Primary worker runtime: **llama.cpp**, **OpenVINO**, or both?

Document answers in this file or `ROADMAP.md` as they land.
