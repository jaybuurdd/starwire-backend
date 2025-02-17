import os
import json
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, APIRouter, HTTPException, Response, status

from utils.logging import logger
from utils.database import get_db
from middleware.session_check import check_user_session
from schemas.users import RegisterRequest, SignInRequest, Account as AccountResponse
from repos.users import UserRepo


router = APIRouter()
# TODO: add request and response models

@router.post("/auth")
async def auth(data: dict, db: Session = Depends(get_db)):
    user_email = data.get("email")
    return UserRepo.otp_auth(user_email, db)

@router.post("/signin")
async def signin(data: SignInRequest, response: Response, db: Session = Depends(get_db)):
    user, session_token = UserRepo.authorize_user_signin(data.model_dump(), db)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=False,
        samesite="lax",
        max_age=86400,
    )

    return user


@router.post("/register")
async def register_user(user : RegisterRequest, response: Response, db: Session = Depends(get_db)):
    user, session_token = UserRepo.reigster_user(user.model_dump(), db)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=False,
        samesite="lax",
        max_age=86400,
    )

    return user


@router.get("/session", dependencies=[Depends(check_user_session)])
async def session_check():
    return Response(status_code=200)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("session_token")
    return Response(status_code=200)