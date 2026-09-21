import sys
import threading
import webbrowser

import uvicorn

from zdli.edge.app import create_edge_app
from zdli.settings import EdgeSettings


def main() -> None:
    es = EdgeSettings()
    url = f"http://127.0.0.1:{es.ui_port}/"
    if es.open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print("ZDLI Edge Client", file=sys.stderr)
    print(f"  UI: {url}", file=sys.stderr)
    uvicorn.run(create_edge_app(), host=es.host, port=es.ui_port, log_level="info")


if __name__ == "__main__":
    main()
