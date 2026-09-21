# Connectors

Pluggable **client-facing** adapters live here. Each connector implements the plugin contract described in [`docs/INTEGRATIONS.md`](../docs/INTEGRATIONS.md).

## Planned packages

| Directory | Role | v1 priority |
|-----------|------|-------------|
| `openai-gateway/` | OpenAI-compatible HTTP server — **Cursor** base URL | **P0** |
| `enterprise-apim/` | Azure APIM policies, backends, identity mapping | **P0** |
| `mcp/` | Model Context Protocol server for agent tools | P2 |

Phase 1 delivers **openai-gateway** and **enterprise-apim** against the same coordinator API. Specifications land here before code.
