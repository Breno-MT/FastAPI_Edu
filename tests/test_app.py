from http import HTTPStatus

def test_root_must_return_ok_and_hello_world(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}

def test_create_new_user_and_check_the_info_success(client):
    response = client.post('/users/create_user', json={
        "username": "testdasilva",
        "email": "testdasilva@gmail.com",
        "password": "1230isoda"
    })
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": response.json().get("id") >=1,
        "username": "testdasilva",
        "email": "testdasilva@gmail.com"
    }

def test_get_users_from_database_success(client):
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "id": 1,
                "username": "testdasilva",
                "email": "testdasilva@gmail.com"
            }
        ]
    }

def test_update_user_from_database_success(client):
    # Must pass an ID on URL
    response = client.put("/users/1", json={
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

    response_get_user = client.get("/users/")
    assert response_get_user.json() == {
        "users": [
            {
                "id": 1,
                "username": "atualizadotest",
                "email": "atualizado@test.com"
            }
        ]
    }

def test_update_user_from_database_failed(client):
    # Must pass an ID on URL
    response = client.put("/users/2", json={
        "username": "atualizadotest",
        "email": "atualizado@test.com",
        "password": "atualizadopasswd"
    })
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
