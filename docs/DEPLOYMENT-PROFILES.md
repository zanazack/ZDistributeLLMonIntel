# Deployment profiles — LAN lab and WAN mesh

v1 supports **both** profiles under one coordinator model. Workers declare a **site** (or region); the scheduler builds pipelines that respect profile rules.

## LAN lab profile

**Use when:** All workers share a low-latency L2/L3 domain (office lab, NUC cluster, training room).

| Attribute | Target |
|-----------|--------|
| RTT between stages | &lt; 2 ms typical |
| Bandwidth | ≥ 10 GbE preferred for 30B+ pipeline |
| Parallelism | Pipeline parallel default; tensor parallel optional |
| Discovery | Static config or mDNS on VLAN |
| Security | mTLS; optional air-gapped (no outbound) |

**Demo path:** 2–8 Intel hosts, ≥10B model (int4/int8), Cursor → local connector → coordinator.

## WAN mesh profile

**Use when:** Workers span **sites** (campus, home office, partner lab) over corporate WAN or Internet.

| Attribute | Target |
|-----------|--------|
| RTT between stages | Site-aware; avoid chaining high-RTT hops on critical path |
| Topology | **Site-local pipelines** with optional **cross-site** shards only when bandwidth SLA met |
| Discovery | Coordinator-centric enrollment; no reliance on broadcast |
| Security | mTLS mandatory; workers **outbound-only** to coordinator where possible |
| Optional overlay | WireGuard / Tailscale / corporate SD-WAN — documented, not required in core |

### WAN scheduling rules (v1)

1. **Prefer intra-site shards** for a session; cross-site only if memory/model graph requires it and SLA allows.
2. **Affinity:** pin returning users to the same site pipeline when KV is site-local.
3. **Degrade gracefully:** queue, reduce max context, or route to cloud fallback (connector policy)—never silent quality collapse.
4. **Activation compression** on WAN links (quantized activations or narrower dtypes) — configurable per link class.

## Shared requirements (both profiles)

- Models **≥10B** parameters for reference testing and docs.
- Workers may run **llama.cpp RPC**, **OpenVINO**, or other registered backends on the same fabric (heterogeneous pools).
- Connectors: **Cursor OpenAI base URL** (dev) and **Azure APIM** (enterprise ingress) — see [`INTEGRATIONS.md`](INTEGRATIONS.md).

## Intel corporate network

Set proxy for control-plane downloads and git (same pattern as IntelAIPoweredCooler):

```powershell
$env:HTTP_PROXY="http://proxy-us.intel.com:911"
$env:HTTPS_PROXY="http://proxy-us.intel.com:911"
```

Data plane between workers on the **same LAN** should use direct paths when policy allows (split horizon).
