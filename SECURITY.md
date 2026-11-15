# Security Policy

## Supported versions

Only the latest commit on the `main` branch is supported. This project is a reference /
demonstration implementation; it is not hardened for production use without additional review.

## Reporting a vulnerability
**Do not open a public issue for security problems.**

Report privately through GitHub's
[private vulnerability reporting](https://github.com/zanazack/ZDistributeLLMonIntel/security/advisories/new)
("Security" tab -> "Report a vulnerability"). If that is unavailable, contact the
maintainer (@zanazack) directly and ask for a private channel.
Please include affected component, version/commit, reproduction steps and impact.
We aim to acknowledge reports within 5 business days.

## Automated security checks

Every pull request runs the `SDL Security Gate` workflow (secret detection, static analysis,
dependency / filesystem / IaC scanning and SBOM generation). Secret-detection findings block
merging; other findings are reported for human triage.

Deployment hardening and security design notes: [`docs/SECURITY.md`](docs/SECURITY.md).
