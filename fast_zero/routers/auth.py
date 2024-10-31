from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter
from sqlalchemy import select

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from fast_zero.database import Session, get_session
from fast_zero.models import User
from fast_zero.security import verify_password, create_access_token
from fast_zero.schemas import Token

T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: T_OAuth2Form,
    session: T_Session
):
    user_db = session.scalar(
        select(User).where(User.username == form_data.username)
    )

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect username or password"
        )

    if not verify_password(form_data.password, user_db.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user_db.username})

    return {"access_token": access_token, "token_type": "Bearer"}
