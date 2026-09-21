import uvicorn

from zdli.gateway.app import create_app
from zdli.settings import GatewaySettings


def main() -> None:
    settings = GatewaySettings()
    uvicorn.run(create_app(), host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
