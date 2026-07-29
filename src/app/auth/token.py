from jose import JWTError, jwt


class InvalidTokenError(Exception):
    pass


def validate_token(token: str, public_key: str) -> dict:
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
    except JWTError:
        raise InvalidTokenError()
    return payload
