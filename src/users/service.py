from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.users import model as um




async def get_user(current_user: um.Users, session: AsyncSession, user_id: int):
    user = (
        await session.execute(
            select(um.Users)
            .where(um.Users.user_id == user_id)
        )
    ).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user


