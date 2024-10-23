from http import HTTPStatus

from fastapi import FastAPI

from .schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

# Temporary fake database to realise some tests
database = []

@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá mundo!"}

@app.post('/users/create_user', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(
        id=len(database) + 1,
        **user.model_dump()
    )
    
    database.append(user_with_id)

    return user_with_id

@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users():
    return {"users": database}

@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    user_with_id = UserDB(
        **user.model_dump(),
        id=user_id
    )
    database[user_id - 1] = user_with_id

    return user_with_id