from pydantic_settings import BaseSettings, SettingsConfigDict


class CoordinatorSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ZDL_COORDINATOR_", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 7443
    api_token: str = "dev-coordinator-token"
    enroll_token: str = "dev-enroll-token"
    public_url: str = ""
    data_dir: str = ""


class ControlCenterSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ZDL_CONTROL_", extra="ignore")

    host: str = "0.0.0.0"
    ui_port: int = 7333
    gateway_port: int = 8080
    coordinator_port: int = 7443
    open_browser: bool = True


class EdgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ZDL_EDGE_", extra="ignore")

    host: str = "127.0.0.1"
    ui_port: int = 7340
    config_path: str = ""
    open_browser: bool = True


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
    enroll_token: str = ""
    worker_id: str = "worker-1"
    site_id: str = "lab"
    heartbeat_seconds: int = 15
    openai_base_url: str | None = None
    rpc_host: str | None = None
    rpc_port: int | None = None
    ram_available_mb: int = 16384
