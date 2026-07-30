"""Validação de tokens JWT emitidos pelo Keycloak.

Estrutura esperada do token (payload), no formato do Keycloak:

    {
        "sub": "<id do usuário>",            # vira user_id
        "azp": "<client de origem>",         # ex.: "analytics-api"; identifica a app
        "resource_access": {                 # client roles, por client
            "analytics-api": {"roles": ["search"]},
            "investigator-api": {"roles": ["search"]}
        },
        "iss": "<issuer do realm>",          # validado no modo keycloak
        "exp": <timestamp>,                  # expiração, validada
        "iat": <timestamp>
    }

Os campos usados pela aplicação: `sub` (identidade), `azp` (app de origem, para
escopo da busca e auditoria) e `resource_access` (permissões, achatadas em
`flatten_permissions`). Assinatura RS256, validada contra a chave pública
(chave local no modo mock; JWKS do Keycloak no modo keycloak).
"""

from jose import JWTError, jwt


class InvalidTokenError(Exception):
    pass


def validate_token(token: str, public_key: str) -> dict:
    """Valida assinatura e expiração do token e retorna o payload decodificado.

    Lança InvalidTokenError se a assinatura for inválida, o token estiver
    expirado ou malformado.
    """
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
    except JWTError:
        raise InvalidTokenError()
    return payload