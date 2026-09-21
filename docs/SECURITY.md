# Security

Distributed inference over commodity endpoints assumes **hostile networks** and **partially trusted** machines. This document outlines controls for ZDistributeLLMonIntel.

## Threat model (summary)

| Threat | Mitigation |
|--------|------------|
| Eavesdropping on prompts/responses | TLS 1.3 everywhere; mTLS on fabric |
| Rogue worker joining pool | Enrollment with PKI; **optional** TEE/attestation (TDX/SGX) for high-assurance tenants |
| Stolen API key at connector | Short-lived tokens, OIDC, rate limits, IP allow lists |
| Prompt injection to exfiltrate shards | Workers never execute client-supplied code; static graphs only |
| Denial of service | Quotas, backpressure, circuit breakers |
| Supply chain (model weights) | Signed manifests, hash verification per shard |

## Encryption

- **Client ↔ Connector:** TLS 1.3 (public or internal CA).
- **Connector ↔ Coordinator:** mTLS; corporate roots via trust store config.
- **Coordinator ↔ Workers:** mTLS; session keys rotated on re-enrollment.
- **At rest:** Encrypted model caches on workers (OS volume encryption + optional app-level keys from HSM/KMS).

## Identity and access

- **Tenants** isolate models, quotas, and audit streams.
- **RBAC:** admin (graph publish), operator (worker drain), user (inference only).
- **Service accounts** for automation with scoped model access.

## Network

- Default: **no public worker ports**; workers initiate outbound to coordinator (NAT-friendly).
- **WAN mesh (v1):** default **TLS-only over Internet**; treat all links as untrusted; mTLS on every hop. **VPN overlay optional** (WireGuard/Tailscale/SD-WAN) per [`DEPLOYMENT-PROFILES.md`](DEPLOYMENT-PROFILES.md)—not required for core operation.
- **APIM path:** terminate customer TLS at APIM; mTLS or private link from APIM to connector/coordinator; subscription keys ≠ worker enrollment certs.

## Proxy / corporate egress

Many Intel environments use HTTP proxies. Components should honor:

```bash
HTTP_PROXY=http://proxy-us.intel.com:911
HTTPS_PROXY=http://proxy-us.intel.com:911
```

- gRPC may require `GRPC_PROXY` or CONNECT tunnel support.
- Document **split horizon**: control plane via proxy; data plane may use direct LAN paths when coordinator and workers share a site.

## Privacy and compliance

- Configurable **zero retention** for prompts/completions.
- Audit logs: metadata only (tenant, model, token counts, latency) by default.
- GDPR/export: tenant-scoped deletion hooks on coordinator metadata stores.

## Roadmap

- [ ] Formal threat model diagram
- [ ] Optional attestation policy pack (TDX/SGX) for tenants that enable it
- [ ] FIPS-compliant cipher suites profile for regulated customers
