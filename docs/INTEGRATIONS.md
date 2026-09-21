# Integrations — pluggable connectors

Goal: **do not fork** Cursor, Gemini, or Microsoft Copilot. Provide **adapters** that make the distributed Intel fabric look like what those tools already support—or like a documented extension point (MCP, LSP, local proxy).

## Integration patterns

| Pattern | Description | Best for |
|---------|-------------|----------|
| **OpenAI-compatible reverse proxy** | Local HTTPS server; clients point `base_url` + API key | Cursor, many CLI tools, LangChain |
| **Sidecar** | Per-user daemon; intercepts only configured hosts | Locked-down corporate laptops |
| **MCP server** | Expose tools/resources + optional model routing | Cursor, Claude Desktop, custom agents |
| **VS Code extension host** | Bridge for Copilot-style custom endpoints | Teams using Azure OpenAI-compatible stacks |
| **Enterprise gateway** | Single ingress, SSO, audit | Copilot Studio / Azure AI Foundry-style routing |

## Cursor

Cursor commonly supports **custom OpenAI-compatible** providers (base URL, model name, API key).

**Connector behavior:**

- Serve `https://127.0.0.1:<port>/v1/chat/completions` (and models list).
- Map `model` field to coordinator **logical model id** (e.g. `intel-distributed-llama-70b-q4`).
- Preserve **streaming** (`text/event-stream`).
- Optional: MCP server for repo-aware tools while inference stays on ZDLI fabric.

**User configuration (conceptual):**

- Override OpenAI base URL to connector.
- API key = connector-issued token (not cloud key).

## Google Gemini

Gemini consumer apps are less openly swappable than IDE OpenAI endpoints. Practical paths:

1. **Gemini API / Vertex** — Connector as **backend router**: for allowed tenants, route specific workloads to on-prem fabric via internal policy (hybrid cloud).
2. **Google AI Studio / API compatibility** — Where clients allow HTTP proxies, same OpenAI-compatible connector pattern may not apply; use **Google’s client libraries** with a **custom transport** only if license and ToS allow routing off Google.
3. **Android / Chrome enterprise** — On-device + LAN fabric for **private** apps using Gemini **SDK** with your own backend that mimics Gemini server-side (legal/compliance review required).

**Recommendation:** Document **hybrid** pattern: Gemini for web-scale features; ZDLI for **code and confidential** prompts via Cursor/CLI routed through connector.

## Microsoft Copilot

Copilot spans M365 (closed) and **extensibility** (Graph, plugins, Azure OpenAI).

**Practical integrations:**

- **Azure OpenAI-compatible** private endpoints: connector registers as custom upstream; Azure API Management or APIM-style policies send selected models to on-prem coordinator.
- **GitHub Copilot** — Limited custom endpoint support; often **enterprise proxy** or **Copilot Business** policies. Fallback: Cursor + ZDLI connector for dev workflows.
- **Windows Copilot / local** — Future: **Windows ML + OpenVINO** workers as edge tier; connector on PC merges local small model + distributed large model.

## Generic OpenAI-compatible clients

Minimum surface for broad compatibility:

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/models` | List logical models on fabric |
| `POST /v1/chat/completions` | Chat + tools (tools optional phase 2) |
| `POST /v1/embeddings` | Optional; often local NPU tier |
| `GET /health` | Connector health |

See [`../protocols/openapi/coordinator-gateway.yaml`](../protocols/openapi/coordinator-gateway.yaml) for a stub.

## Connector plugin interface (conceptual)

Future code may implement:

```text
ConnectorPlugin
  name() -> str
  client_protocols() -> ["openai-v1", "mcp", ...]
  authenticate(request) -> TenantContext
  map_model(client_model_id) -> LogicalModelId
  forward_completion(ctx, payload) -> Stream[Token]
  fallback_policy(ctx) -> Optional[CloudBackend]
```

Plugins ship as separate packages (e.g. `zdl-connector-cursor`, `zdl-connector-apim`).

## Security notes for integrations

- Connectors must **not** log prompt content by default in enterprise mode; configurable redaction.
- API keys are **connector-scoped**, rotatable, mappable to LDAP/OIDC groups.
- mTLS from connector to coordinator; optional device cert for worker pools.

## Next steps

Prioritize one **golden path**: e.g. Cursor + OpenAI-compatible connector + 2-node LAN demo. Expand to APIM and MCP once streaming path is stable.
