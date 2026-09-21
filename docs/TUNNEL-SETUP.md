# Tunnel setup (required path) — Cloudflare quick tunnels

Use this when you **cannot** publish a public IP or corporate reverse proxy. Remote edge PCs only need **outbound HTTPS** to the tunnel hostname.

## Overview

| Local service | Port | Tunnel | Used by |
|---------------|------|--------|---------|
| Control Center + coordinator | **7443** | Tunnel **A** | **ZDL Edge** on all remote PCs |
| OpenAI gateway | **8080** | Tunnel **B** | Optional: Cursor on a machine **outside** this PC |

If **Cursor runs only on the control PC**, skip Tunnel B and use `http://127.0.0.1:8080/v1` locally.

## 1. Install cloudflared (control PC)

**Windows (winget)** — if `.ps1` scripts are blocked, use the `.cmd` wrapper or bypass for this session only:

```powershell
# Option A — no execution-policy change (recommended)
.\scripts\install-cloudflared.cmd

# Option B — one PowerShell session only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\install-cloudflared.ps1

# Option C — direct winget (no script)
winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
```

Or download: [Cloudflare cloudflared releases](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

**Ubuntu:**

```bash
# See Cloudflare docs for your distro; example .deb from GitHub releases
cloudflared --version
```

Corporate proxy (Intel network) for **install only**:

```powershell
$env:HTTPS_PROXY="http://proxy-us.intel.com:911"
```

Runtime tunnel traffic usually goes **direct** to Cloudflare, not via corporate proxy.

## 2. Start Control Center first

```powershell
cd C:\Users\zanailha\DEV\ZDistributeLLMonIntel
$env:ZDL_COORDINATOR_ENROLL_TOKEN = "your-enroll-secret"
$env:ZDL_COORDINATOR_API_TOKEN = "your-admin-secret"
$env:ZDL_GATEWAY_COORDINATOR_TOKEN = $env:ZDL_COORDINATOR_API_TOKEN
.\Start-ZDLI-ControlCenter.cmd
```

Confirm: http://127.0.0.1:7443/ui

## 3. Open tunnels (two terminals)

**Terminal T1 — coordinator (required for edge nodes):**

```powershell
cloudflared tunnel --url http://127.0.0.1:7443
```

Copy the HTTPS URL shown (example shape):

`https://abc-def-123.trycloudflare.com`

**No `:7443` suffix** — cloudflared terminates HTTPS on 443 and forwards to local 7443.

**Terminal T2 — gateway (optional):**

```powershell
cloudflared tunnel --url http://127.0.0.1:8080
```

Copy the second URL for remote Cursor/APIM if needed.

Or run the helper (opens two **CMD** windows that **stay open**; logs under `%USERPROFILE%\.zdli\logs\`):

```powershell
.\scripts\start-wan-tunnels.cmd
```

**Order matters:** start Control Center **before** tunnels. If tunnel windows vanish, Control Center was not running on `:7443` or corporate **HTTP_PROXY** broke cloudflared (the wrapper clears proxy for the tunnel process).

## 4. Save URLs in Control Center

Open http://127.0.0.1:7443/ui → **WAN linking**

| Field | Value |
|-------|--------|
| **Public coordinator URL** | Tunnel T1 URL exactly, e.g. `https://abc-def-123.trycloudflare.com` |
| **Public gateway URL** | Tunnel T2 URL or `http://127.0.0.1:8080` if Cursor is local only |

Click **Save public URLs**.

Copy **Enroll token** from the same page.

## 5. Configure each remote Edge client

On each Windows/Ubuntu corporate PC → http://127.0.0.1:7340

| Field | Value |
|-------|--------|
| Coordinator URL | **Same as Tunnel T1** (https://….trycloudflare.com) |
| Enroll token | From control dashboard |
| Worker ID | Unique per machine |

Click **Save & connect**. Within ~15s the control dashboard should show the worker **ready**.

**Test from edge PC (optional):**

```powershell
curl.exe https://YOUR-TUNNEL.trycloudflare.com/health
```

Expect: `{"status":"ok"}`

## 6. Stability notes

- **Quick tunnels** are for **lab/PoC**; URLs **change** when cloudflared restarts. Re-save in Control Center and update edge clients.
- For longer tests, use a [named Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) with a fixed hostname.
- Keep **T1** running whenever edge nodes should stay connected.

## 7. Firewall checklist

| Location | Requirement |
|----------|-------------|
| Control PC | Allow **outbound** to Cloudflare; allow local 7443/8080 |
| Corporate edge PCs | Allow **outbound HTTPS** to `*.trycloudflare.com` (or your fixed tunnel host) |
| Corporate edge PCs | **No inbound** ports required |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tunnel window closes in seconds | Start `Start-ZDLI-ControlCenter.cmd` first; read `%USERPROFILE%\.zdli\logs\tunnel-7443.log` |
| `ERROR: Nothing listening on 7443` | Control Center not running — start it, wait for dashboard in browser |
| Proxy / Intel network | Tunnel script clears `HTTP_PROXY` for cloudflared; if still failing, IT may block outbound to Cloudflare — try off VPN or personal hotspot test |
| Edge registration failed | Coordinator URL must match tunnel T1; enroll token must match `ZDL_COORDINATOR_ENROLL_TOKEN` |
| SSL / certificate errors | Use the `https://` URL from cloudflared, not `http://127.0.0.1:7443` on remote PCs |
| Tunnel dropped | Restart cloudflared; update URLs on all edge clients |

Manual debug (one window, stays open):

```powershell
.\scripts\run-cloudflared-tunnel.cmd 7443
```

See also: [`WAN-CLUSTER-SETUP.md`](WAN-CLUSTER-SETUP.md)
