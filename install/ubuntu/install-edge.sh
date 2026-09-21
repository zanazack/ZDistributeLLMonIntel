#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "ZDLI Edge Client installer (Linux)"
command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
cd "$ROOT"
python3 -m pip install --user -e .
cat > "$HOME/.zdli/start-edge.sh" <<'EOF'
#!/usr/bin/env bash
exec zdl-edge
EOF
chmod +x "$HOME/.zdli/start-edge.sh"
echo "Run: $HOME/.zdli/start-edge.sh"
echo "UI: http://127.0.0.1:7340"
