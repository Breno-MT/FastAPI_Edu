from http import HTTPStatus
from jwt import decode

from fast_zero.security import create_access_token, SECRET_KEY, ALGORITHM


def test_create_jwt():
    data = {
        "sub": "test"
    }
    result = create_access_token(data)
    decoded_result = decode(result, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_result["sub"] == data["sub"]
    assert decoded_result["exp"]

def test_get_token_success(client, user):
    response = client.post("/token", data={
        "username": user.username,
        "password": user.clean_password
    })
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token

def test_get_token_failed(client, user):
    response = client.post("/token", data={
        "username": user.username,
        "password": user.email
    })

    assert response.json().get("detail") == "Incorrect username or password"
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_jwt_invalid_token(client):
    response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer invalid-token"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get("detail") == "Could not validate credentials"
