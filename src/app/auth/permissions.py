"""Mapeamento de client roles do Keycloak para permissões da aplicação.

O Keycloak emite as roles por client em `resource_access.<client>.roles`.
Esta camada achata essa estrutura aninhada em um conjunto plano de permissões
no formato "<app>:<role>", que é o que o restante da aplicação usa.

Exemplo:
    resource_access = {"analytics-api": {"roles": ["search"]}}
    -> {"analytics:search"}

Clients não mapeados em CLIENT_TO_APP (ex.: "account", clients internos do
Keycloak) são ignorados.
"""

CLIENT_TO_APP = {
    "analytics-api": "analytics",
    "investigator-api": "investigator",
    "case-manager-api": "case-manager",
}


def flatten_permissions(resource_access: dict) -> set[str]:
    """Achata `resource_access` do token em um conjunto de permissões "<app>:<role>".

    Clients ausentes de CLIENT_TO_APP são ignorados.
    """
    permissions: set[str] = set()
    for client_id, access in resource_access.items():
        app_prefix = CLIENT_TO_APP.get(client_id)
        if app_prefix is None:
            continue
        for role in access.get("roles", []):
            permissions.add(f"{app_prefix}:{role}")
    return permissions