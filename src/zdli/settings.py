from pydantic_settings import BaseSettings, SettingsConfigDict


class CoordinatorSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ZDL_COORDINATOR_", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 7443
    api_token: str = "dev-coordinator-token"


class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ZDL_GATEWAY_", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8080
    coordinator_url: str = "http://127.0.0.1:7443"
    coordinator_token: str = "dev-coordinator-token"
    api_key: str = "dev-gateway-key"


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ZDL_WORKER_", extra="ignore")

    coordinator_url: str = "http://127.0.0.1:7443"
    coordinator_token: str = "dev-coordinator-token"
    worker_id: str = "worker-1"
    site_id: str = "lab"
    heartbeat_seconds: int = 15
    openai_base_url: str | None = None
    rpc_host: str | None = None
    rpc_port: int | None = None
    ram_available_mb: int = 16384
