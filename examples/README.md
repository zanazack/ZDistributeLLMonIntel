# Examples

Planned examples (Phase 1):

| Example | Profile | Model class | Client |
|---------|---------|-------------|--------|
| `two-node-lan/` | LAN lab | ≥10B via llama.cpp RPC | Cursor → openai-gateway |
| `openvino-single-site/` | LAN lab | ≥10B OpenVINO IR | APIM or gateway |
| `two-site-wan/` | WAN mesh | ≥10B, site-biased shards | APIM + Cursor |
| `proxy-env/` | Both | — | Intel HTTP proxy for control plane |

Placeholder until Phase 1 implementations exist.
