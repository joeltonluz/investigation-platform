import httpx
from jose import JWTError, jwk, jwt

from app.auth.token import InvalidTokenError


class JWKSFetcher:
    def __init__(self, jwks_url: str):
        self._jwks_url = jwks_url
        self._keys: dict[str, dict] = {}

    @classmethod
    def with_keys(cls, keys: dict[str, dict]) -> "JWKSFetcher":
        fetcher = cls.__new__(cls)
        fetcher._jwks_url = ""
        fetcher._keys = keys
        return fetcher

    async def get_key(self, kid: str) -> dict | None:
        if kid not in self._keys:
            self._keys = await self._fetch_jwks()
        return self._keys.get(kid)

    async def _fetch_jwks(self) -> dict[str, dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(self._jwks_url)
            response.raise_for_status()
            data = response.json()
        keys: dict[str, dict] = {}
        for key_data in data.get("keys", []):
            kid = key_data.get("kid")
            if kid:
                keys[kid] = key_data
        return keys


async def validate_token_with_jwks(
    token: str, fetcher: JWKSFetcher, issuer: str
) -> dict:
    headers = jwt.get_unverified_headers(token)
    kid = headers.get("kid")
    if not kid:
        raise InvalidTokenError()

    key_data = await fetcher.get_key(kid)
    if not key_data:
        raise InvalidTokenError()

    key = jwk.construct(key_data)
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_exp": True, "verify_iss": True, "verify_aud": False},
            issuer=issuer,
        )
    except JWTError:
        raise InvalidTokenError()

    return payload
