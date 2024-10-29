from http import HTTPStatus
from typing import Annotated
from sqlalchemy import select, func

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.security import get_current_user, get_password_hash
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
              
def get_users(session: T_Session,
              current_user : T_CurrentUser,
              limit: int = 10,
              offset: int = 0):

    users_db = session.scalars(
        select(User).limit(limit).offset(offset)
    )
    return {"users": users_db}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic,)
def get_user(user_id: int,
             session: T_Session,
             current_user : T_CurrentUser):
    user_db = session.scalar(
        select(User).where(User.id == user_id)
    )
    
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    
    return user_db


@router.post('/create_user', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema,
                session: T_Session):
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


@router.put('/{user_id}', response_model=UserPublic)
def update_user(user_id: int,
                user: UserSchema,
                session: T_Session,
                current_user : T_CurrentUser):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permission"
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)
    current_user.updated_at = func.now()
    
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(user_id: int,
                session: T_Session,
                current_user : T_CurrentUser):
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permission"
        )
    
    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted successfully.'}
