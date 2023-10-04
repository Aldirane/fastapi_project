from datetime import timedelta

from src.api.config.models.auth import AuthConfig


def load_auth(dct: dict) -> AuthConfig:
    return AuthConfig(
        secret_key=dct["secret-key"],
        token_expire=timedelta(hours=dct["access-token-expire-hours"])
    )
