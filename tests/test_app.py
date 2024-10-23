from http import HTTPStatus
from fastapi.testclient import TestClient
from fast_zero.app import app

client = TestClient(app)


def test_root_must_return_ok_and_hello_world():
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}

def test_create_new_user_and_check_the_info():
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
