from http import HTTPStatus
from jwt import decode, encode

from fast_zero.security import create_access_token, settings


def test_create_jwt():
    data = {
        "sub": "test"
    }
    result = create_access_token(data)
    decoded_result = decode(result, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_result["sub"] == data["sub"]
    assert decoded_result["exp"]

def test_get_token_success(client, user):
    response = client.post("/auth/token", data={
        "username": user.username,
        "password": user.clean_password
    })
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token

def test_get_token_failed(client, user):
    response = client.post("/auth/token", data={
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

def test_validate_token_after_user_delete(client, user):
    response = client.post("/auth/token", data={
        "username": user.username,
        "password": user.clean_password
    })
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token

    second_response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer {token["access_token"]}"}
    )

    assert second_response.status_code == HTTPStatus.OK
    assert second_response.json() == {'message': 'User deleted successfully.'}

    third_response = client.get("/users/",
                                 headers={"Authorization": f"Bearer {token["access_token"]}"})

    assert third_response.status_code == HTTPStatus.UNAUTHORIZED
    assert third_response.json().get("detail") == "Could not validate credentials"

def test_token_no_sub_username(client, token):
    token = decode(token.get("Authorization")[7:], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    token.pop("sub")
    new_token = encode(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    response = client.get("/users/", headers={"Authorization": f"Bearer {new_token}"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get("detail") == "Could not validate credentials"
