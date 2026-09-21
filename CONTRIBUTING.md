# Contributing

Thank you for helping build distributed LLM inference on Intel endpoints.

## Process

1. Open an issue or discuss in an existing design doc under `docs/`.
2. Keep changes focused; match the architecture in `docs/ARCHITECTURE.md`.
3. Do not commit secrets, model weights, or `.env` files.

## Development environment

Behind Intel corporate network, configure proxy when needed:

```powershell
$env:HTTP_PROXY="http://proxy-us.intel.com:911"
$env:HTTPS_PROXY="http://proxy-us.intel.com:911"
```

## Code style

To be defined when implementation languages are chosen. Prefer small, reviewable PRs.
