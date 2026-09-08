from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.users import model as um, schemas as um_schemas
from sqlalchemy.exc import IntegrityError



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


async def get_user_by_phone(phone: str, session: AsyncSession):
    user = (
        await session.execute(
            select(um.Users)
            .where(um.Users.phone == phone)
        )
    ).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user


async def search_users(q: str, current_user: um.Users, session: AsyncSession, limit: int = 12):
    query = q.strip()
    if len(query) < 1:
        return []

    pattern = f"%{query}%"
    users = await session.execute(
        select(um.Users)
        .where(
            or_(
                um.Users.name.ilike(pattern),
                um.Users.phone.ilike(pattern),
                um.Users.email.ilike(pattern),
            )
        )
        .order_by(um.Users.name)
        .limit(limit)
    )
    return [
        user
        for user in users.scalars().all()
        if user.user_id != current_user.user_id
    ]


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
        
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with these credentials already exists")
    await session.refresh(user)
    return user



async def delete_user(user_id: int, current_user: um.Users, session: AsyncSession):
    if current_user.user_id != user_id and current_user.role != um.RoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action")

    user = (
        await session.execute(select(um.Users).where(um.Users.user_id == user_id))
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await session.delete(user)
    await session.commit()
    return user