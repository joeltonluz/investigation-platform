import os

os.environ["AUTH_MODE"] = "mock"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://investigation:password@localhost:5432/investigation",
)

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.db.base import Base

engine = create_engine(Settings().database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_key, public_key_pem


@pytest.fixture
def token_factory(rsa_keypair):
    private_key, _ = rsa_keypair

    def _factory(
        sub: str = "user-123",
        azp: str = "analytics-api",
        resource_access: dict | None = None,
        exp: int | None = None,
    ) -> str:
        import time

        payload = {
            "sub": sub,
            "azp": azp,
            "resource_access": resource_access or {},
            "iat": int(time.time()),
            "exp": exp or int(time.time()) + 3600,
        }
        return jwt.encode(payload, private_key, algorithm="RS256")

    return _factory
