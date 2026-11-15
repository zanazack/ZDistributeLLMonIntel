# AGENTS.md

The canonical, always-on policy for every AI coding agent working in this repository
(GitHub Copilot, Claude, Codex, Cursor and others) is
[`.github/copilot-instructions.md`](.github/copilot-instructions.md). Read and follow it before
making any change.
Quick rules:

- Do not commit secrets, credentials, tokens or customer data.
- Do not weaken, skip or disable the `SDL Security Gate` workflow or other checks.
- Changes to prompts, agent/tool definitions, authentication or authorization, or
  `.github/` require review by the code owners (@zanazack).
- Stop and ask for human approval before any material, destructive, financial, identity,
  deployment or production-changing action.
- Report vulnerabilities as described in [`SECURITY.md`](SECURITY.md).
