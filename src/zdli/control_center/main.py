from __future__ import annotations

import sys
import threading
import time
import webbrowser

import uvicorn

from zdli.control_center.app import create_control_app
from zdli.gateway.app import create_app as create_gateway_app
from zdli.settings import ControlCenterSettings, CoordinatorSettings, GatewaySettings


def _run_gateway() -> None:
    gs = GatewaySettings()
    gs.host = "0.0.0.0"
    uvicorn.run(create_gateway_app(), host=gs.host, port=gs.port, log_level="warning")


def main() -> None:
    cs = ControlCenterSettings()
    coord = CoordinatorSettings()
    coord.host = "0.0.0.0"
    port = cs.coordinator_port

    gw_thread = threading.Thread(target=_run_gateway, daemon=True)
    gw_thread.start()
    time.sleep(0.5)

    if cs.open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}/ui")).start()

    print("ZDLI Control Center", file=sys.stderr)
    print(f"  Dashboard:  http://127.0.0.1:{port}/ui", file=sys.stderr)
    print(f"  Coordinator: http://127.0.0.1:{port}/zdl/v1/ (edge nodes connect here)", file=sys.stderr)
    print(f"  Gateway:     http://127.0.0.1:{cs.gateway_port}/v1/ (Cursor / APIM)", file=sys.stderr)
    print("  WAN: expose ports 7443 + 8080 — docs/WAN-CLUSTER-SETUP.md", file=sys.stderr)

    uvicorn.run(create_control_app(), host=coord.host, port=port, log_level="info")


if __name__ == "__main__":
    main()
