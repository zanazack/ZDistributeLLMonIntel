# Deployment profiles — LAN lab and WAN mesh

v1 supports **both** profiles. They differ in **which execution modes** are default ([`ARCHITECTURE.md`](ARCHITECTURE.md)).

## LAN lab profile

**Use when:** Store, branch, office, classroom, lab, or home LAN — RTT between nodes typically **&lt; 2 ms**, bandwidth **≥ 1 GbE** (10 GbE preferred for 32B pipeline).

| Default modes | 1 (replicas), 5 (routing), **2–4 when admitted** |
| Model-distributed | **Yes** — primary home for **Qwen2.5-32B** pipeline and speculative verify |
| Discovery | Static config or mDNS on VLAN |
| Security | mTLS; optional air-gap |

**Phase 2 target:** 2–8 Intel hosts, pipeline or speculative paths with benchmark proof ([`BENCHMARKS.md`](BENCHMARKS.md)).

## WAN mesh profile

**Use when:** Workers span sites over **TLS-only Internet** (VPN **optional** overlay).

| Default modes | **1 (replicas per site)**, **5 (semantic/policy routing)** |
| Model-distributed pipeline | **Not default** — autoregressive ITL penalizes slow hops; only with admission control + compression + explicit SLA |
| Topology | Site-local replica pools; cross-site **routing**, not layer chaining on hot path |
| Discovery | Coordinator enrollment; outbound worker connections |
| Security | mTLS mandatory; private trust domain for sensitive prompts |

### WAN scheduling rules

1. Route requests to **best site replica** or SLM tier by latency, load, and policy.
2. **Do not** place sequential pipeline stages across high-RTT links unless benchmarks show net ITL win.
3. **Affinity** for site-local KV when using single-node large models per site.
4. **Degrade:** queue, SLM, or cloud fallback — never silent quality collapse.

## Shared requirements

- Catalog includes **≥10B** class; reference **[Qwen2.5-32B-Instruct](REFERENCE-MODEL.md)**.
- Workers: **llama.cpp**, **OpenVINO/OVMS**, extensible manifests.
- Clients: **Cursor** + **APIM** golden paths.

## Intel corporate network

```powershell
$env:HTTP_PROXY="http://proxy-us.intel.com:911"
$env:HTTPS_PROXY="http://proxy-us.intel.com:911"
```

Control-plane downloads via proxy; **same-LAN data plane** should use direct paths when policy allows.
