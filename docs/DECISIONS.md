# Product decisions (v1)

Locked choices for the first implementation wave. Update this file when decisions change; link from PRs that implement them.

| Decision | Choice | Implications |
|----------|--------|--------------|
| **North star** | **One large LLM across many Intel edge devices** | Partition weights and inference **tasks** (layers/blocks/experts) so models **≥10B** run where **no single device** has enough RAM or capability |
| **Cloud dependency** | **Minimum** — edge-first | OpenAI gateway for existing tools; **optional** cloud fallback for overload/outage only, not primary path |
| **Deployment scope** | **LAN lab + WAN mesh** across sites | Same goal: compose **one logical model** from many endpoints; WAN uses admission control + compression because ITL is RTT-sensitive |
| **Not the core product** | **Workload-distributed “full model per PC”** | Running a **complete** small LLM on each machine for concurrency scaling is a **different problem**; this repo may integrate tiny helpers (embeddings, optional draft) but **does not** optimize for fleet-of-SLMs as the main value |
| **Minimum model class** | **10B parameters and larger** | Sharding is mandatory for target class; reference **Qwen2.5-32B-Instruct** ([`REFERENCE-MODEL.md`](REFERENCE-MODEL.md)) |
| **Worker runtimes** | **llama.cpp RPC**, **OpenVINO**, **extensible** | Backends execute **shards**, not only whole models |
| **Golden-path clients** | **Cursor (OpenAI base URL)** and **enterprise APIM** | One logical sharded model exposed as familiar API |
| **Repo visibility** | **Public open source** | Apache 2.0 |
| **TEE / attestation** | **Optional** | Default: PKI + mTLS |
| **WAN transport default** | **TLS-only over public Internet** | VPN **optional** |

See [`ROADMAP.md`](ROADMAP.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`MISSION.md`](MISSION.md).
