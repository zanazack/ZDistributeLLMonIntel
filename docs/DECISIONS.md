# Product decisions (v1)

Locked choices for the first implementation wave. Update this file when decisions change; link from PRs that implement them.

| Decision | Choice | Implications |
|----------|--------|--------------|
| **Deployment scope** | **LAN lab + WAN mesh** across sites | Two profiles from day one: low-latency site pools and multi-site graphs with stricter SLA and relay options |
| **Minimum model class** | **10B parameters and larger** | Sharding, memory planning, and demos target ≥10B; **reference demo uses 32B** (see below) |
| **Worker runtimes** | **llama.cpp RPC**, **OpenVINO**, **extensible** | Coordinator matches artifacts to runtime via capability matrix; additional backends (IPEX, vLLM-CPU, etc.) plug in without changing client contracts |
| **Golden-path clients** | **Cursor (OpenAI base URL)** and **enterprise APIM** | Phase 1 delivers local OpenAI-compatible connector *and* APIM policy/upstream templates in parallel |
| **Repo visibility** | **Public open source** | Apache 2.0; no proprietary-only core; enterprise features (SSO, audit) as documented add-ons |
| **TEE / attestation** | **Optional** | Default trust: **PKI enrollment + mTLS**; Intel TDX/SGX or other attestation as an **opt-in** worker profile for regulated tenants |
| **WAN transport default** | **TLS-only over public Internet** | Workers/coordinator use mTLS on TCP (443 or configured port); no VPN required |
| **WAN VPN overlay** | **Optional** | WireGuard, Tailscale, corporate SD-WAN documented in [`DEPLOYMENT-PROFILES.md`](DEPLOYMENT-PROFILES.md); operators may add overlay without forking core |
| **Reference model (≥16B)** | **Qwen2.5-32B-Instruct** | Canonical HF id, quants, logical model names: [`REFERENCE-MODEL.md`](REFERENCE-MODEL.md) |

See [`ROADMAP.md`](ROADMAP.md) for delivery phases and [`ARCHITECTURE.md`](ARCHITECTURE.md) for technical consequences.
