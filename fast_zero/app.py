from http import HTTPStatus
from sqlalchemy import select, func

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from .database import get_session
from .models import User
from .security import get_password_hash, verify_password
from .schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


@app.get('/token')
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session = Depends(get_session)
):
    user_db = session.scalar(
        select(User).where(User.username == form_data.username)
    )

    if not user_db or verify_password(form_data.password, user_db.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect username or password"
        )
    
    return user_db

@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá mundo!"}

@app.post('/users/create_user', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Username/Email already on Database"
        )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(limit: int = 10, offset: int = 0, session = Depends(get_session)):
    users_db = session.scalars(
        select(User).limit(limit).offset(offset)
    )
    return {"users": users_db}

@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(user_id: int, session = Depends(get_session)):
    user_db = session.scalar(
        select(User).where(User.id == user_id)
    )
    
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    
    return user_db

@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema, session = Depends(get_session)):

    user_db = session.scalar(
        select(User).where(User.id == user_id)
    )

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    user_db.username = user.username
    user_db.email = user.email
    user_db.password = get_password_hash(user.password)
    user_db.updated_at = func.now()

    session.commit()
    session.refresh(user_db)

    return user_db

@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session = Depends(get_session)):
    user_db = session.scalar(
        select(User).where(User.id == user_id)
    )

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    
    session.delete(user_db)
    session.commit()

    return {'message': 'User deleted successfully.'}
