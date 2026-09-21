# Connectors

Pluggable **client-facing** adapters live here. Each connector implements the plugin contract described in [`docs/INTEGRATIONS.md`](../docs/INTEGRATIONS.md).

## Planned packages

| Directory | Role |
|-----------|------|
| `openai-gateway/` | OpenAI-compatible HTTP server (golden path) |
| `mcp/` | Model Context Protocol server for agent tools |
| `enterprise-apim/` | Policies and docs for Azure API Management |

Implementations will be added in Phase 1+. This folder currently holds specifications only.
