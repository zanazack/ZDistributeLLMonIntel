# Integrations — pluggable connectors

Goal: **do not fork** Cursor, Gemini, or Microsoft Copilot. Provide **adapters** that make the distributed Intel fabric look like what those tools already support—or like a documented extension point (MCP, LSP, local proxy).

## v1 golden paths (both required in Phase 1)

| Path | Audience | Entry |
|------|----------|--------|
| **Cursor + OpenAI base URL** | Developers, labs | Local or team `openai-gateway` connector |
| **Enterprise APIM** | IT, security, chargeback | Azure API Management in front of same OpenAI-compatible surface |

Both paths hit the same coordinator and **≥10B** logical models on the LAN/WAN fabric. APIM adds SSO, rate limits, IP filters, and audit; Cursor uses direct connector URL + API key.

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
- Map `model` field to coordinator **logical model id** (e.g. `intel-distributed-qwen2.5-32b-q4` — **10B+** only in v1 catalogs).
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

## Enterprise Azure APIM (v1 golden path)

APIM is the **enterprise front door** for the same OpenAI-compatible API the Cursor connector uses.

**Reference shape:**

```
Client / internal app → APIM (OAuth/JWT, quotas, logging)
                      → ZDLI connector or coordinator gateway (/v1/*)
                      → Coordinator → workers (LAN site and/or WAN mesh)
```

**Deliverables in `connectors/enterprise-apim/`:**

- Policy fragments: route `model` names matching `intel-distributed-*` to ZDLI backend
- Backend entity pointing at connector URL (on-prem or VNet)
- Optional cloud fallback backend with `<choose>` on HTTP 503 / policy header
- Correlation id passthrough for audit (metadata only by default)

**Identity:** Map APIM subscription or Entra ID claims to coordinator **tenant id** for quotas and model ACLs.

## Microsoft Copilot

Copilot spans M365 (closed) and **extensibility** (Graph, plugins, Azure OpenAI).

**Practical integrations:**

- **Azure OpenAI-compatible** private endpoints: same APIM golden path—policies send selected models to ZDLI upstream instead of Azure OpenAI.
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

Plugins ship as separate packages (e.g. `zdl-connector-openai-gateway`, `zdl-connector-apim`).

## Security notes for integrations

- Connectors must **not** log prompt content by default in enterprise mode; configurable redaction.
- API keys are **connector-scoped**, rotatable, mappable to LDAP/OIDC groups.
- mTLS from connector to coordinator; optional device cert for worker pools.

## Next steps

Implement **Cursor** and **APIM** paths in parallel on a shared OpenAI gateway; validate on **LAN lab** first, then **WAN mesh** with two labeled sites. MCP and Gemini hybrid remain Phase 4.
