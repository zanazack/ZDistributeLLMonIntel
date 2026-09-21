# WAN cluster setup — 1 control PC + remote Windows/Ubuntu nodes

## How linking works (corporate firewalls)

Remote machines **do not** need inbound ports opened. Each **ZDL Edge** client makes **outbound HTTPS** to your **coordinator** URL.

```
[Control PC — your desk]
  Control Center :7443 (coordinator + dashboard /ui)
  Gateway        :8080 (OpenAI API for Cursor)

[Corporate PC A — Windows]     ──outbound HTTPS──┐
[Corporate PC B — Windows]     ──outbound HTTPS──┼──► Coordinator (public URL)
[Corporate PC C — Ubuntu]      ──outbound HTTPS──┘
```

You **do not** SSH from the control PC into corporate PCs for registration. Install **ZDL Edge** on each remote system; paste the same **Coordinator URL** and **enroll token** from the dashboard.

### What you must expose (control PC or cloud hop)

The **control PC** (or a small cloud VM running Control Center) must be reachable from the Internet on:

| Port | Service |
|------|---------|
| **7443** | Coordinator + dashboard (`/ui`) |
| **8080** | OpenAI gateway (optional on control PC if you only use Cursor there locally) |

Corporate networks usually allow **outbound** HTTPS to approved hosts. Publish a **public HTTPS URL** (DNS or tunnel) pointing to your control machine.

## Step 1 — Control PC (this computer)

### Install

```powershell
cd C:\Users\zanailha\DEV\ZDistributeLLMonIntel
.\install\windows\Install-ZDLI-Control.ps1
```

Edit `zdl.env` or set environment variables:

```powershell
$env:ZDL_COORDINATOR_API_TOKEN = "choose-a-long-admin-secret"
$env:ZDL_COORDINATOR_ENROLL_TOKEN = "choose-a-long-enroll-secret"
$env:ZDL_GATEWAY_API_KEY = "cursor-gateway-key"
$env:ZDL_GATEWAY_COORDINATOR_TOKEN = $env:ZDL_COORDINATOR_API_TOKEN
```

Start:

```powershell
.\Start-ZDLI-ControlCenter.cmd
```

Open **http://127.0.0.1:7443/ui**

### Expose to the Internet (pick one)

**A — IT-approved reverse proxy / load balancer**  
Forward `https://zdl.yourcompany.com` → control PC `7443` and `8080`.

**B — Quick lab tunnel (Cloudflare)**  
Install [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/), then:

```powershell
cloudflared tunnel --url http://127.0.0.1:7443
```

Copy the printed `https://….trycloudflare.com` URL → paste into Control Center **Public coordinator URL** (add `/zdl/v1` base: use root `https://xxx.trycloudflare.com` — edge uses `/zdl/v1/workers/register` on that host).

Run a **second** tunnel for port 8080 if Cursor runs off-machine.

**C — Azure / AWS small VM**  
Run Control Center on a VM with public IP; lock down admin tokens.

In the dashboard **WAN linking** section, save:

- **Public coordinator URL** — e.g. `https://zdl.example.com:7443`
- **Public gateway URL** — e.g. `https://zdl.example.com:8080`

Share **enroll token** with edge installs (not the admin API token).

## Step 2 — Each remote machine (2× Windows, 1× Ubuntu)

### Windows (corporate)

Copy repo or `pip install git+https://github.com/zanazack/ZDistributeLLMonIntel.git` if outbound GitHub is allowed.

```powershell
# From repo clone
.\install\windows\Install-ZDLI-Edge.ps1
.\Start-ZDLI-Edge.cmd
```

Browser: **http://127.0.0.1:7340**

1. **Coordinator URL** — public URL from step 1 (must reach `:7443` path prefix)
2. **Enroll token** — from Control Center (not admin token)
3. **Worker ID** — unique (`win-branch-01`, `win-branch-02`, `ubuntu-nuc-01`)
4. **Site ID** — e.g. `wan-east`, `wan-west`
5. Click **Save & connect** — status should become **ready**

If proxy is required on corporate PCs:

```powershell
$env:HTTP_PROXY="http://proxy-us.intel.com:911"
$env:HTTPS_PROXY="http://proxy-us.intel.com:911"
```

### Ubuntu

```bash
cd ZDistributeLLMonIntel
bash install/ubuntu/install-edge.sh
~/.zdli/start-edge.sh
```

Same UI fields as Windows.

## Step 3 — Confirm cluster on control PC

Dashboard → **Registered edge nodes** — all three workers **healthy**.

Click **Auto-build shard graph from workers** (orders workers by registration; set **ingress** `openai_base_url` on one node when llama-server runs).

## Step 4 — llama.cpp on each node (user-controlled)

Edge UI **does not** silently download multi-GB models. You choose paths:

| Node role | Typical process |
|-----------|-----------------|
| RPC shard | `llama-rpc-server` + GGUF path |
| Ingress | `llama-server` + `--rpc remote:port` |

Update **OpenAI base URL** / **RPC port** in Edge UI when ready; agent sends updates on heartbeat.

## Step 5 — Cursor on control PC

- Base URL: `http://127.0.0.1:8080/v1` (or public gateway URL)
- API key: `ZDL_GATEWAY_API_KEY`
- Model: `intel-distributed-qwen2.5-32b-instruct-q4`

## OS support

| OS | Control Center | Edge Client |
|----|----------------|-------------|
| Windows 10/11 | Yes | Yes |
| Ubuntu 22.04+ | Yes | Yes |

Same Python package (`zdli`); llama.cpp binaries are OS-specific.

## Security notes

- **Enroll token** — share only with your edge machines; rotate in `zdl.env`.
- **Admin token** — dashboard / graph changes only; never put on edge nodes.
- WAN sharding sends **activations** between nodes — use private trust domain; mTLS hardening is on the roadmap.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| Edge **error** on register | Coordinator URL reachable from edge browser? Try `curl https://…/health` |
| Worker offline | Heartbeat blocked by firewall/proxy? |
| Cursor 503 | Graph missing or ingress `openai_base_url` empty |
| Slow tokens over WAN | Expected for cross-site pipeline — see admission control in [`BENCHMARKS.md`](BENCHMARKS.md) |
