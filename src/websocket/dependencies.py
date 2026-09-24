from fastapi import Query, Depends, HTTPException, status
from src.db.database import  get_db
from src.users import model as um
from src.auth import dependencies, utils
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.redis import check_jti_blocked


async def get_current_user(
    token = Query(...),
    session: AsyncSession = Depends(get_db)
):
    token = utils.verify_token(token)
    from src.main import app
    redis = app.state.redis
    
    if await check_jti_blocked(redis, token["jti"],token['user']["user_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    
    token = await dependencies.AccessTokenRequired(token)
    
    user_id = int(token['user']["user_id"])
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = (
        await session.execute(
            select(um.Users)
            .where(um.Users.user_id == user_id)
        )
    ).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action")
    
    
    return user

def role_checker(allowed_rows: list, is_verified: None = False):
    async def check(
        current_user: um.Users = Depends(get_current_user)
    ):
        if current_user.role not in allowed_rows:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action")
        
        if is_verified and not current_user.is_verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action")
        return current_user
    return check