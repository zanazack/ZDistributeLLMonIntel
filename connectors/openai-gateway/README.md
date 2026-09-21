# OpenAI-compatible gateway

Implementation lives in Python package **`zdli.gateway`** (`zdl-gateway` console script).

- Source: [`src/zdli/gateway/`](../../src/zdli/gateway/)
- Resolves **sharded** logical models via the coordinator, proxies to ingress **llama-server** (or OVMS OpenAI surface)
- Example: [`examples/lan-pipeline-32b/`](../../examples/lan-pipeline-32b/)
