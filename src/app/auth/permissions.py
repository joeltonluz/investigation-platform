CLIENT_TO_APP = {
    "analytics-api": "analytics",
    "investigator-api": "investigator",
    "case-manager-api": "case-manager",
}


def flatten_permissions(resource_access: dict) -> set[str]:
    permissions: set[str] = set()
    for client_id, access in resource_access.items():
        app_prefix = CLIENT_TO_APP.get(client_id)
        if app_prefix is None:
            continue
        for role in access.get("roles", []):
            permissions.add(f"{app_prefix}:{role}")
    return permissions
