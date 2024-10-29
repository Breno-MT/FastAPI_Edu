import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import table_registry, User
from fast_zero.security import get_password_hash


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={'check_same_thread':False},
        poolclass=StaticPool
    )
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)

@pytest.fixture()
def user(session):
    pwd = "test123"
    user = User(
        username="test",
        email="test@gmail.com",
        password=get_password_hash(pwd)
    )

    user.clean_password = pwd
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@pytest.fixture()
def token(client, user):
    response = client.post(
        "/auth/token",
        data={
            "username": user.username,
            "password": user.clean_password
        }
    )
    return {"Authorization": f"Bearer {response.json()["access_token"]}"}
