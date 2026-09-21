import uvicorn

from zdli.coordinator.app import create_app
from zdli.settings import CoordinatorSettings


def main() -> None:
    settings = CoordinatorSettings()
    uvicorn.run(create_app(), host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
