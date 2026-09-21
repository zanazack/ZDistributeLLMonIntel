# Mission — distribute one LLM across Intel edge devices

## Problem

Commodity Intel endpoints (PCs, POS, kiosks, workstations, store servers) **cannot** run today’s large LLMs alone: insufficient **RAM**, GPU/NPU memory, and thermal headroom. Cloud inference works but drives **cost**, **latency**, **privacy**, and **dependency**.

## What this project is

**ZDistributeLLMonIntel** is an **edge-first** fabric that runs **one logical large language model** by **dividing the model into shards/tasks** across **many devices**:

- Each worker holds **part of the weights** (pipeline stage, tensor shard, or expert subset).
- Workers exchange **activations**, **KV segments**, or **collective ops** over an encrypted fabric protocol (**ZDLI / EIFP**).
- Clients see a **single model** via OpenAI-compatible **gateway** (Cursor, APIM, etc.).

The install base becomes a **virtual large-model machine** without requiring datacenter GPUs on every desk.

## What this project is not (primary scope)

| Approach | Why it is not the main goal |
|----------|-----------------------------|
| **Workload-distributed inference** | Putting a **full** 7B/8B model on every PC scales **requests**, not **model size**; it does not solve “this 32B model cannot fit here.” |
| **Cloud-first hybrid** | Cloud may exist as **break-glass fallback**; success is measured by **edge tokens**, not cloud offload rate. |

Optional adjuncts (still on-edge): small **draft** models for speculative decoding (Mode 4), **embedding** shards on NPUs—these **accelerate** the distributed large model; they do not replace sharding.

## Success criteria

- **Qwen2.5-32B-Instruct** (and similar **≥16B** models) complete inference with **no single node holding the full weights**.
- **Least cloud dependency** for steady-state GenAI on Intel fleet.
- **Pluggable** into existing tools without forking IDEs.

Research context (hybrid strategies, papers): [`FINDINGS.md`](FINDINGS.md) — the **product** stays model-distributed first.
