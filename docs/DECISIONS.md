# Product decisions (v1)

Locked choices for the first implementation wave. Update this file when decisions change; link from PRs that implement them.

| Decision | Choice | Implications |
|----------|--------|--------------|
| **Deployment scope** | **LAN lab + WAN mesh** across sites | Two profiles from day one: low-latency site pools and multi-site graphs with stricter SLA and relay options |
| **Minimum model class** | **10B parameters and larger** | Sharding, memory planning, and demos target ≥10B (e.g. 14B–70B class), not sub-10B-only |
| **Worker runtimes** | **llama.cpp RPC**, **OpenVINO**, **extensible** | Coordinator matches artifacts to runtime via capability matrix; additional backends (IPEX, vLLM-CPU, etc.) plug in without changing client contracts |
| **Golden-path clients** | **Cursor (OpenAI base URL)** and **enterprise APIM** | Phase 1 delivers local OpenAI-compatible connector *and* APIM policy/upstream templates in parallel |
| **Repo visibility** | **Public open source** | Apache 2.0; no proprietary-only core; enterprise features (SSO, audit) as documented add-ons |

## Still open (not blocking v1 scaffold)

- Mandatory **TEE/attestation** (SGX/TDX) vs optional enrollment-only trust
- Default **WAN transport** preference: mesh VPN overlay vs TLS-only over public Internet
- First **reference model** artifact (exact HF id, quant, and shard count for lab demo)

See [`ROADMAP.md`](ROADMAP.md) for delivery phases and [`ARCHITECTURE.md`](ARCHITECTURE.md) for technical consequences.
