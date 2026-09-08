from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status
from src.auth import utils
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from sqlalchemy import select
from src.users import model as um
from src.db.redis import check_jti_blocked


bearer_scheme = HTTPBearer()
async def verify_token(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
      token = utils.verify_token(creds.credentials)
      from src.main import app
      
      redis = app.state.redis
      if await check_jti_blocked(redis, token["jti"], int(token["user"]["user_id"])):
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
      
      return token


def verify_raw_token(token: str):
      return utils.verify_token(token)
  
async def AccessTokenRequired(token):
    if token['refresh']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is required")
    return token

async def GainRefreshToken(token = Depends(verify_token)):
    if not token['refresh']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required")
    return token

async def RefreshTokenRequired(token):
    if not token["refresh"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required")
    return token

async def get_current_user(token = Depends(verify_token), session: AsyncSession = Depends(get_db)):
    token = await AccessTokenRequired(token)
    user_id = token['user']["user_id"]
    
    
    user = (
        await session.execute(select(um.Users).where(um.Users.user_id ==user_id ))
    ).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action iii")
    
    return user


def role_checker(allowed_roles: list, is_verified: bool = False):
    
    async def check(
        current_user: um.Users = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action ii")
        
        if is_verified and not current_user.is_verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action ii")
        
        return current_user
    return check
    