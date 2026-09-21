# Benchmark plan

Do **not** optimize for tokens/sec alone. Autoregressive, multi-hop, and fleet-churn behaviors dominate user experience and cost.

## Per-request latency

- Time to first token (TTFT)
- Inter-token latency (ITL) — mean and distribution
- p50 / p95 / p99 end-to-end latency
- Tokens per second **per request** (not only aggregate)

## Throughput and efficiency

- Aggregate tokens per second across fleet
- **Joules per token** (or wall power proxy)
- Idle-fleet utilization (% enrolled endpoints doing useful inference)
- Cloud tokens avoided vs baseline (metered at connector)

## Distribution-specific

- **Bytes transmitted per generated token** (activations, KV moves, speculative batches)
- Model-load and **shard recovery** time
- Performance under packet **loss and jitter**
- Node join / leave / sleep / Wi-Fi change recovery time
- **Output equivalence** vs single-node reference (same model, same prompt set)

## Fleet and thermal

- Endpoint temperature and throttling events during sustained load
- Failure rate when endpoints depart mid-session

## Economic

- Cost per million tokens (fabric + amortized hardware vs cloud list price)

## Scenarios (minimum matrix)

| Scenario | Mode | Network |
|----------|------|---------|
| Single replica baseline | Mode 1 | N/A |
| Semantic routing SLM → large | Mode 5 | LAN |
| Qwen2.5-32B pipeline 2–8 nodes | Mode 2 | LAN lab |
| Two-site **replica** pools | Mode 1 + routing | WAN TLS-only |
| Two-site **pipeline** (stretch) | Mode 2 | WAN — expect ITL regression; document |
| Speculative draft + verify | Mode 4 | LAN |
| Adverse: +50 ms RTT hop | Any | Emulated |

## Admission control validation

For each candidate worker added to a pipeline, record:

- Δ ITL, Δ TTFT, Δ bytes/token
- **Reject** addition if p95 ITL regresses beyond SLA ([`ARCHITECTURE.md`](ARCHITECTURE.md))

## Tooling (Phase 1+)

- Harness in `examples/` (future): fixed prompt suite, reproducible seeds, JSON metrics export for CI regression (non-flaky thresholds on LAN simulators only).

Reference motivation: edge network characterization showing multi-node regressions — see [`FINDINGS.md`](FINDINGS.md).
