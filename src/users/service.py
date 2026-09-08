from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.users import model as um, schemas as um_schemas




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


async def get_users(current_user: um.Users, session: AsyncSession):
    
    users = (
        await session.execute(
            select(um.Users)
            
        )
    ).scalars().all()
    
    if not users: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    return users


async def update_user(credentials: um_schemas.UserUpdate, user_id: int, current_user: um.Users, session: AsyncSession):
    if current_user.user_id != user_id and current_user.role != um.RoleEnum.SUPER_ADMIN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action")
        
    user = (
        await session.execute(
            select(um.Users)
            .where(um.Users.user_id == user_id)
        )
    ).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    for key, value in  credentials.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
        
    await session.commit()
    await session.refresh(user)
    return user



async def delete_user(user_id: int, current_user: um.Users, session: AsyncSession):
    if current_user.user_id != user_id and current_user.role != um.RoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action")