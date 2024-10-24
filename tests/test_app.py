from http import HTTPStatus

def test_root_must_return_ok_and_hello_world(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}

def test_create_new_user_and_check_the_info(client):
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

def test_get_users_from_database(client):
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