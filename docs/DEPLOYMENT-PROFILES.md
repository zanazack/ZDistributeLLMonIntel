# Deployment profiles — LAN lab and WAN mesh

Both profiles serve **model-distributed** inference: **one LLM, many shards**. Neither profile prioritizes “full small model on every PC.”

## LAN lab profile

**Use when:** Office, store backroom, classroom, lab, home — low RTT between shards.

| Attribute | Target |
|-----------|--------|
| RTT between stages | &lt; 2 ms typical |
| Bandwidth | ≥ 1 GbE (10 GbE for 32B pipeline) |
| Sharding | **Pipeline default** — 2–8 nodes, **Qwen2.5-32B** reference |
| Goal | Prove **no single node** holds full model; measure ITL |

## WAN mesh profile

**Use when:** Edge nodes across sites must **collectively** host one large model (aggregate RAM across geography).

| Attribute | Target |
|-----------|--------|
| Default transport | **TLS-only Internet**, mTLS |
| VPN | **Optional** overlay — not required |
| Sharding | **Same logical model** — minimize **cross-WAN hops** per token; prefer dense sub-pipelines per site + limited cross-site stages |
| Admission | **Required** — drop or shrink graph if RTT makes ITL unacceptable |
| Not default | WAN is not an excuse to run **independent full SLMs** per site as the product story |

### WAN placement rules

1. Place as many **consecutive layers** as possible **within one site** before crossing WAN.
2. Compress activations on inter-site links.
3. **Do not** substitute cloud for steady-state if edge graph is viable (cloud = optional fallback).

## Shared

- Reference model: [`REFERENCE-MODEL.md`](REFERENCE-MODEL.md)
- Runtimes: llama.cpp RPC, OpenVINO/OVMS
- Clients: Cursor, APIM

## Intel proxy

```powershell
$env:HTTP_PROXY="http://proxy-us.intel.com:911"
$env:HTTPS_PROXY="http://proxy-us.intel.com:911"
```

Control plane via proxy; prefer direct LAN paths for activation traffic inside a site.
