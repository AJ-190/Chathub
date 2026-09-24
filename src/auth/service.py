from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.auth import schemas, utils, dependencies
from sqlalchemy.ext.asyncio import AsyncSession
from src.users import model as um
from src.auth.utils import Token
from src.db.redis import block_jti, check_jti_blocked
from datetime import datetime, timezone


async def sign_up(credentials: schemas.UserCreateAccount, session: AsyncSession):
    user = um.Users(
        name=credentials.name.strip(),
        phone=credentials.phone.strip(),
        email=credentials.email.strip().lower() if credentials.email else None,
        password=utils.hash(credentials.password.get_secret_value()),
    )
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )


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
    



async def logout(token: schemas.RefreshLogoutToken, current_user: um.Users, session: AsyncSession):
    
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
    
    expire = token["exp"] - int(datetime.now(timezone.utc).timestamp())
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    
    await block_jti(redis_, jti, user_id, expire)
    return "Logout successfullt"
    