from fastapi import HTTPException, status
from sqlalchemy import select, or_
from src.auth import schemas, utils, dependencies
from sqlalchemy.ext.asyncio import AsyncSession
from src.users import model as um
from src.auth.utils import Token
from src.db.redis import block_jti
from datetime import datetime, timezone


async def sign_up(credentials: schemas.UserCreateAccount, session: AsyncSession):
    user_exist = (

            select(um.Users)
            .where(um.Users.phone == credentials.phone)

        )
    if credentials.email:
        user_exist.where(um.Users.email == credentials.email)
    
    exist = (await session.execute(user_exist)).scalar_one_or_none()
    if exist:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exist")
    
    user = um.Users(**credentials.model_dump(exclude=['password', "role"]), password=utils.hash(credentials.password.get_secret_value()))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def login(credentials  ,session: AsyncSession):
    user = (await session.execute(select(um.Users).where(um.Users.phone == credentials.username))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not registered")
    
    if not utils.verify(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect phone or password")
    
    user_data = {"user_id": user.user_id, "role": user.role.value}
    access_token = Token(user_data, refresh=False)
    refresh_token = Token(user_data, refresh=True)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "type": "Bearer"
    }
    

async def logout(token: schemas.RefreshLoginToken, current_user: um.Users, session: AsyncSession):
    
    from src.main import app
    redis_ = app.state.redis
    token = dependencies.RefreshTokenRequired(token)
    user_id = token["user"]["user_id"]
    jti = token['jti']
    
    user = (
        await session.execute(
            select(um.Users)
            .where(um.Users.user_id == user_id)
        )
    ).scalar_one_or_none()
    
    expire = token["exp"] - datetime.now(timezone.utc).timestamp()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    
    await block_jti(redis_, jti, user_id, expire)
    return "Logout successfullt"
    