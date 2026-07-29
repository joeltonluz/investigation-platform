from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = ""
    public_key: str = ""

    auth_mode: str = "keycloak"
    keycloak_issuer: str = ""

    @property
    def keycloak_jwks_url(self) -> str:
        if self.keycloak_issuer:
            return f"{self.keycloak_issuer}/protocol/openid-connect/certs"
        return ""
