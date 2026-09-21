#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "ZDLI Control Center installer (Linux)"
command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
cd "$ROOT"
python3 -m pip install --user -e .
mkdir -p "$HOME/.zdli"
if [[ ! -f "$ROOT/zdl.env" ]]; then cp "$ROOT/zdl.env.example" "$ROOT/zdl.env"; fi
cat > "$HOME/.zdli/start-control.sh" <<EOF
#!/usr/bin/env bash
export ZDL_COORDINATOR_HOST=0.0.0.0
exec zdl-control-center
EOF
chmod +x "$HOME/.zdli/start-control.sh"
echo "Run: $HOME/.zdli/start-control.sh"
echo "Dashboard: http://127.0.0.1:7443/ui"
