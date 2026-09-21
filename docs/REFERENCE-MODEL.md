# Reference model (v1)

First **canonical** model for lab demos, CI smoke (future), and connector catalog entries. Must satisfy **≥16B** parameters and broad real-world adoption.

**Phase 1 target:** **Pipeline-sharded** across **≥2 edge workers** — **no worker stores the full 32B weights**. Cloud fallback is **optional** break-glass only ([`MISSION.md`](MISSION.md), [`ROADMAP.md`](ROADMAP.md)).

## Primary: Qwen2.5-32B-Instruct

| Field | Value |
|-------|--------|
| **Hugging Face** | [`Qwen/Qwen2.5-32B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct) |
| **Parameters** | 32B (dense) |
| **License** | Apache 2.0 |
| **Why this model** | Top-tier open-weight usage for **general + code** workloads; strong community support, GGUF artifacts for llama.cpp, and OpenVINO/HF export paths; fits the **16B+** bar while remaining a practical distributed demo (vs 70B first) |

### Logical IDs (connector / APIM)

| Surface | Id |
|---------|-----|
| OpenAI `model` field | `intel-distributed-qwen2.5-32b-instruct-q4` |
| Short alias | `qwen2.5-32b-zdli` |

### Artifacts by runtime

**llama.cpp RPC (lab default)**

- Format: **GGUF**
- Quantization: **Q4_K_M** (balance of quality and RAM on Intel CPU pools)
- Obtain: community GGUF builds aligned with upstream Qwen2.5 tokenizer/chat template, or convert from HF with documented tooling in Phase 1 examples
- Chat template: Qwen2.5 Instruct (harmony with HF `tokenizer_config.json`)

**OpenVINO**

- Format: OpenVINO IR or runtime-supported export from HF checkpoint (Phase 1 worker documents exact opset and minimum OpenVINO version)
- Start with **CPU** plugin on Xeon/Core; GPU/NPU optional in Phase 3 scheduling

### Suggested sharding (starting points)

Tune to actual RAM per host; these are **planning defaults**, not hard limits.

| Profile | Hosts | Notes |
|---------|-------|--------|
| LAN lab | 4 × pipeline stages | ~8B params equivalent weight per stage at Q4_K_M order-of-magnitude |
| LAN minimal | 2 × pipeline stages | Requires high-RAM boxes or Q3_K; mark as **stretch** in docs |
| WAN mesh | 2 sites × 2 stages each | Site-local pairs; cross-site only for admin/rebalance, not per-token hot path |

Manifest fields (future `protocols/`): `model_id`, `hf_revision`, `gguf_sha256`, `stage_index`, `stage_count`, `runtime: llama.cpp-rpc | openvino`.

## Alternates (not v1 canonical)

Use for stretch goals or A/B; same coordinator catalog mechanism.

| Model | HF id | Notes |
|-------|--------|--------|
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` | Very high adoption; gated license; heavier WAN/LAN footprint |
| Gemma 2 27B IT | `google/gemma-2-27b-it` | Strong 16B+ option; license terms differ from Apache |
| Qwen2.5-14B-Instruct | `Qwen/Qwen2.5-14B-Instruct` | Below 16B — **out of v1 reference** but OK for dev smoke only |

## Client examples

**Cursor** — set model to `intel-distributed-qwen2.5-32b-instruct-q4`.

**APIM** — route policies match `intel-distributed-qwen*` or exact id above.

See [`INTEGRATIONS.md`](INTEGRATIONS.md) and [`examples/README.md`](../examples/README.md).
