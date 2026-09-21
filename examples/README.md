# Examples

Planned examples (Phase 1):

| Example | Profile | Model class | Client |
|---------|---------|-------------|--------|
| `two-node-lan/` | LAN lab | **Qwen2.5-32B-Instruct** Q4 GGUF, llama.cpp RPC | Cursor → openai-gateway |
| `openvino-single-site/` | LAN lab | Same model, OpenVINO export | APIM or gateway |
| `two-site-wan/` | WAN mesh, **TLS-only** (VPN optional) | Qwen2.5-32B, site-biased shards | APIM + Cursor |
| `proxy-env/` | Both | — | Intel HTTP proxy for control plane |

Placeholder until Phase 1 implementations exist.
