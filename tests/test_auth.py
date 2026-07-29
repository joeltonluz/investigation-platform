import pytest
from fastapi import Depends
from jose import jwt

from app.auth.permissions import flatten_permissions
from app.auth.token import InvalidTokenError, validate_token


class TestValidateToken:
    def test_valid_token_returns_payload(self, token_factory, rsa_keypair):
        _, public_key_pem = rsa_keypair
        token = token_factory(sub="user-456", azp="investigator-api")
        payload = validate_token(token, public_key_pem)
        assert payload["sub"] == "user-456"
        assert payload["azp"] == "investigator-api"

    def test_invalid_signature_raises_error(self, rsa_keypair):
        from cryptography.hazmat.primitives.asymmetric import rsa as rsa_mod

        _, public_key_pem = rsa_keypair
        other_key = rsa_mod.generate_private_key(65537, 2048)
        bad_token = jwt.encode({"sub": "u1"}, other_key, algorithm="RS256")
        with pytest.raises(InvalidTokenError):
            validate_token(bad_token, public_key_pem)

    def test_expired_token_raises_error(self, rsa_keypair, token_factory):
        import time

        _, public_key_pem = rsa_keypair
        expired_token = token_factory(exp=int(time.time()) - 60)
        with pytest.raises(InvalidTokenError):
            validate_token(expired_token, public_key_pem)

    def test_malformed_token_raises_error(self, rsa_keypair):
        _, public_key_pem = rsa_keypair
        with pytest.raises(InvalidTokenError):
            validate_token("not-a-jwt", public_key_pem)


class TestFlattenPermissions:
    def test_single_app_single_role(self):
        result = flatten_permissions({"analytics-api": {"roles": ["search"]}})
        assert result == {"analytics:search"}

    def test_multiple_apps_and_roles(self):
        result = flatten_permissions(
            {
                "analytics-api": {"roles": ["search", "export"]},
                "investigator-api": {"roles": ["search"]},
            }
        )
        assert result == {"analytics:search", "analytics:export", "investigator:search"}

    def test_unknown_client_ignored(self):
        result = flatten_permissions({"unknown-client": {"roles": ["admin"]}})
        assert result == set()

    def test_empty_roles_produces_no_permissions(self):
        result = flatten_permissions({"analytics-api": {"roles": []}})
        assert result == set()


class TestGetCurrentUser:
    def test_valid_token_returns_user(self, rsa_keypair, token_factory):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.auth.dependencies import get_current_user, get_public_key

        _, public_key_pem = rsa_keypair

        app = FastAPI()

        @app.get("/me")
        async def me(user=Depends(get_current_user)):
            return {
                "user_id": user.user_id,
                "app_client_id": user.app_client_id,
                "permissions": sorted(user.permissions),
            }

        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="u1",
            azp="analytics-api",
            resource_access={
                "analytics-api": {"roles": ["search"]},
            },
        )

        client = TestClient(app)
        resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == "u1"
        assert data["app_client_id"] == "analytics-api"
        assert "analytics:search" in data["permissions"]

    def test_missing_token_returns_401(self, rsa_keypair):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.auth.dependencies import get_current_user, get_public_key

        _, public_key_pem = rsa_keypair

        app = FastAPI()

        @app.get("/me")
        async def me(user=Depends(get_current_user)):
            return {"ok": True}

        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        client = TestClient(app)
        resp = client.get("/me")

        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, rsa_keypair):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.auth.dependencies import get_current_user, get_public_key

        _, public_key_pem = rsa_keypair

        app = FastAPI()

        @app.get("/me")
        async def me(user=Depends(get_current_user)):
            return {"ok": True}

        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        client = TestClient(app)
        resp = client.get("/me", headers={"Authorization": "Bearer invalid"})

        assert resp.status_code == 401


class TestRequirePermission:
    def test_permission_present_passes(self, rsa_keypair, token_factory):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.auth.dependencies import (
            get_public_key,
            require_permission,
        )

        _, public_key_pem = rsa_keypair

        app = FastAPI()

        @app.get("/search")
        async def search(user=Depends(require_permission("analytics:search"))):
            return {"ok": True}

        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="u1",
            azp="analytics-api",
            resource_access={
                "analytics-api": {"roles": ["search"]},
            },
        )

        client = TestClient(app)
        resp = client.get("/search", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200

    def test_permission_absent_returns_403(self, rsa_keypair, token_factory):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.auth.dependencies import (
            get_public_key,
            require_permission,
        )

        _, public_key_pem = rsa_keypair

        app = FastAPI()

        @app.get("/search")
        async def search(user=Depends(require_permission("analytics:search"))):
            return {"ok": True}

        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="u1",
            azp="analytics-api",
            resource_access={
                "analytics-api": {"roles": ["export"]},
            },
        )

        client = TestClient(app)
        resp = client.get("/search", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 403
