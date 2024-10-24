from http import HTTPStatus

from fastapi import FastAPI, HTTPException

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

@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(user_id: int):
    user_with_id = None
    for user in database:
        if user.id == user_id:
            user_with_id = user
    
    if not user_with_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    
    return user_with_id

@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):

    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    user_with_id = UserDB(
        **user.model_dump(),
        id=user_id
    )
    database[user_id - 1] = user_with_id

    return user_with_id

@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    del database[user_id - 1]

    return {'message': 'User deleted successfully.'}
