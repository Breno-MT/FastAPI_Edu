from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_create_new_user_and_check_the_info_success(client, token):
    response = client.post('/users/create_user', headers=token, json={
        "username": "testdasilva",
        "email": "testdasilva@gmail.com",
        "password": "1230isoda"
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 2,
        "username": "testdasilva",
        "email": "testdasilva@gmail.com"
    }

def test_create_new_user_and_duplicate_him_username(client, token):
    response = client.post('/users/create_user', headers=token, json={
        "username": "testdasilva",
        "email": "testdasilva@gmail.com",
        "password": "1230isoda"
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 2,
        "username": "testdasilva",
        "email": "testdasilva@gmail.com"
    }

    second_response = client.post('/users/create_user', headers=token, json={
        "username": "testdasilva",
        "email": "testdasilvaaa@gmail.com",
        "password": "1230isoda"
    })
    assert second_response.status_code == HTTPStatus.CONFLICT
    assert second_response.json().get("detail") == "Username/Email already on Database"

def test_create_new_user_and_duplicate_him_email(client, token):
    response = client.post('/users/create_user', headers=token, json={
        "username": "testdasilvaaaa",
        "email": "testdasilva@gmail.com",
        "password": "1230isoda"
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 2,
        "username": "testdasilvaaaa",
        "email": "testdasilva@gmail.com"
    }

    second_response = client.post('/users/create_user', headers=token, json={
        "username": "testdasilva",
        "email": "testdasilva@gmail.com",
        "password": "1230isoda"
    })
    assert second_response.status_code == HTTPStatus.CONFLICT
    assert second_response.json().get("detail") == "Username/Email already on Database"

def test_get_users_from_database_success(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/", headers=token)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [user_schema]
    }

def test_get_user_by_id_success(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(f'/users/{user.id}', headers=token)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema

def test_get_user_by_id_failed(client, token):
    response = client.get('/users/2', headers=token)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}

def test_update_user_from_database_success(client, user, token):
    # Must pass an ID on URL
    response = client.put(f"/users/{user.id}", 
    headers=token,
    json={
        "username": "atualizadotest",
        "email": "atualizado@test.com",
        "password": "atualizadopasswd"
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "atualizadotest",
        "email": "atualizado@test.com",
    }

    response_token = client.post(
        "/auth/token",
        data={
            "username": "atualizadotest",
            "password": "atualizadopasswd"
        }
    )
    response_get_user = client.get("/users/",
        headers={
            "Authorization": f"Bearer {response_token.json()["access_token"]}"
            })

    assert response_get_user.json() == {
        "users": [
            {
                "id": 1,
                "username": "atualizadotest",
                "email": "atualizado@test.com"
            }
        ]
    }

def test_update_user_from_database_failed(client, token):
    # Must pass an ID on URL
    response = client.put("/users/2", headers=token, json={
        "username": "atualizadotest",
        "email": "atualizado@test.com",
        "password": "atualizadopasswd"
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permission'}

def test_delete_user_success(client, user, token):
    response = client.delete('/users/1', headers=token)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully.'}

def test_delete_user_failed(client, token):
    response = client.delete('/users/2', headers=token)
    assert response.status_code == HTTPStatus.BAD_REQUEST