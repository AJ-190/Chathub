from fastapi import APIRouter, Depends, HTTPException
from src.auth import schemas
from src.db.database import get_db
from sqlalchemy import select
from src.db import redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import service as auth_service
from src.users import model as um, service as um_service
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from src.auth import dependencies, utils
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=['Authentication'])

roles = {um.RoleEnum.USER, um.RoleEnum.SUPER_ADMIN}

@router.post("/sign_up", response_model=schemas.UserCreateResponse)
async def sign_up(credentials: schemas.UserCreateAccount,
                  session: AsyncSession = Depends(get_db)):
    return await auth_service.sign_up(credentials, session)


@router.post("/login", response_model=schemas.TokenReponse)
async def login(credentials: OAuth2PasswordRequestForm = Depends(), 
                session: AsyncSession = Depends(get_db)):
    return await auth_service.login(credentials, session)

@router.post("/refresh", response_model=schemas.TokenReponse)
async def refresh(
                  session: AsyncSession = Depends(get_db),
                  refresh_token: dict = Depends(dependencies.GainRefreshToken)):
    from src.main import app
    redis_ = app.state.redis
    
    user_id = refresh_token['user']['user_id']
    user = (
        await session.execute(
            select(um.Users)
            .where(um.Users.user_id == user_id)
        )
    ).scalar_one_or_none()
    
    expire = refresh_token['exp'] - int(datetime.now(timezone.utc).timestamp())
    
    await redis.block_jti(redis_, refresh_token['jti'], user_id, expire)
    token_data = {"user_id": user.user_id, "role": user.role.value}
    
    refresh_token = utils.Token(token_data, refresh=True)
    access_token = utils.Token(token_data, refresh=False)
    
    return{
        "refresh_token": refresh_token,
        "access_token": access_token,
        "type": "Bearer"
    }
    

@router.post("/logout", status_code=204)
async def logout(token: schemas.RefreshLogoutToken,current_user = Depends(dependencies.role_checker([*roles])),
                 session = Depends(get_db)):
    return auth_service.logout()