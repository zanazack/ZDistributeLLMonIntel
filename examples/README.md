# Examples

All examples target **model-distributed** inference (one LLM, many shards) unless noted as helper-only.

| Example | Phase | Profile | Focus |
|---------|-------|---------|--------|
| `lan-pipeline-32b/` | 1 | LAN | **Qwen2.5-32B** llama.cpp RPC, 2+ shards, Cursor gateway |
| `openvino-sharded-stage/` | 1 | LAN | OpenVINO stage(s) on Intel CPU/GPU |
| `cursor-apim/` | 1 | Both | Golden-path clients to **same sharded model id** |
| `two-site-wan-shards/` | 1–2 | WAN TLS-only | Shards across sites + admission control |
| `speculative-sharded/` | 2 | LAN | Draft helper + sharded 32B verifier |
| `proxy-env/` | 1 | Both | Intel HTTP proxy for enrollment/downloads |

Placeholder until implementations land.
