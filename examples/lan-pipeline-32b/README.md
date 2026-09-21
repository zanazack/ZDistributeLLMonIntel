# LAN pipeline — Qwen2.5-32B (llama.cpp RPC)

Run the **ZDLI control plane** on one machine, **llama.cpp RPC workers** on two or more edge hosts, and point **Cursor** at the local OpenAI gateway.

## Prerequisites

- Python 3.11+ with `pip install -e ".[dev]"` from repo root
- [llama.cpp](https://github.com/ggerganov/llama.cpp) built with RPC support on each edge host
- GGUF for [`Qwen2.5-32B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct) (e.g. Q4_K_M), same file path or synced copy per host
- Enough **aggregate RAM** across hosts; no single node holds the full model when RPC split is configured

## 1. Start coordinator and gateway (control machine)

```powershell
$env:ZDL_COORDINATOR_API_TOKEN = "dev-coordinator-token"
$env:ZDL_GATEWAY_API_KEY = "dev-gateway-key"
$env:ZDL_GATEWAY_COORDINATOR_URL = "http://127.0.0.1:7443"

# Terminal A
zdl-coordinator

# Terminal B
zdl-gateway
```

## 2. Edge host A — RPC server (shard worker)

```bash
# Example: rpc-server exposing backend on port 50052
./llama-rpc-server -m /path/to/qwen2.5-32b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 50052
```

Register with coordinator (from host A or control machine):

```powershell
$env:ZDL_WORKER_WORKER_ID = "shard-0"
$env:ZDL_WORKER_SITE_ID = "lab"
$env:ZDL_WORKER_RPC_HOST = "192.168.1.10"
$env:ZDL_WORKER_RPC_PORT = "50052"
$env:ZDL_WORKER_COORDINATOR_URL = "http://192.168.1.100:7443"
zdl-worker
```

## 3. Edge host B — ingress llama-server + RPC to host A

Start RPC attachment per llama.cpp docs, then OpenAI-compatible server:

```bash
# Example flags — adjust to your llama.cpp version
./llama-server -m /path/to/qwen2.5-32b-instruct-q4_k_m.gguf \
  --host 0.0.0.0 --port 8081 \
  --rpc 192.168.1.10:50052
```

Register ingress worker:

```powershell
$env:ZDL_WORKER_WORKER_ID = "shard-1"
$env:ZDL_WORKER_OPENAI_BASE_URL = "http://192.168.1.11:8081"
$env:ZDL_WORKER_COORDINATOR_URL = "http://192.168.1.100:7443"
zdl-worker
```

## 4. Publish shard graph

```powershell
python examples/lan-pipeline-32b/bootstrap_graph.py `
  --coordinator http://127.0.0.1:7443 `
  --token dev-coordinator-token
```

## 5. Cursor

- **Base URL:** `http://127.0.0.1:8080/v1` (or APIM upstream to same)
- **API key:** `dev-gateway-key`
- **Model:** `intel-distributed-qwen2.5-32b-instruct-q4`

Traffic flow: Cursor → **zdl-gateway** → coordinator session → **llama-server** on ingress → RPC → remote shards.

## Docker (coordinator + gateway only)

```bash
docker compose -f examples/lan-pipeline-32b/docker-compose.yml up
```

llama.cpp remains on bare-metal Intel edge nodes in Phase 1.

## Intel proxy

```powershell
$env:HTTP_PROXY="http://proxy-us.intel.com:911"
$env:HTTPS_PROXY="http://proxy-us.intel.com:911"
```

Use for Hugging Face downloads, not for LAN activation traffic between shards.
