"""
Expected JWT payload structure (Keycloak RS256).

The token is an RS256-signed JWT with the following claims:

- ``sub`` (str): Unique user identifier (e.g. ``"user-123"``).
- ``azp`` (str): Authorized party — the Keycloak client that issued the
  token (e.g. ``"analytics-api"``, ``"investigator-api"``,
  ``"case-manager-api"``).
- ``resource_access`` (dict): Keycloak client roles, keyed by client ID::

    {
      "<client-id>": {
        "roles": ["<role1>", "<role2>"]
      }
    }

- ``exp`` (int): Expiration time (Unix epoch seconds).
- ``iat`` (int): Issued-at time (Unix epoch seconds).

Permissions are derived by flattening ``resource_access`` through a
centralised client-id-to-app-prefix mapping (see :mod:`app.auth.permissions`).
"""
