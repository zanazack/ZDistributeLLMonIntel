from fastapi import Header, HTTPException, status

from zdli.settings import CoordinatorSettings


def bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bearer token required")
    return authorization.removeprefix("Bearer ").strip()


def verify_admin(authorization: str | None = Header(default=None)) -> None:
    token = bearer_token(authorization)
    settings = CoordinatorSettings()
    if token != settings.api_token:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid admin token")


def verify_worker_or_admin(authorization: str | None = Header(default=None)) -> None:
    token = bearer_token(authorization)
    settings = CoordinatorSettings()
    if token in (settings.api_token, settings.enroll_token):
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid token")
