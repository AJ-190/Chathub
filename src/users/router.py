from fastapi import APIRouter, Depends
from src.users import service as service, model as um
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import schemas ,dependencies
from src.db.database import get_db


router = APIRouter(prefix="/users", tags=['Users'])

@router.get("/get/user/{user_id}", response_model=schemas.UserCreateResponse)
async def get_user(user_id: int, current_user: um.Users = Depends(dependencies.role_checker([um.RoleEnum.SUPER_ADMIN, um.RoleEnum.USER])) , 
                   session: AsyncSession = Depends(get_db)):
    
    return await service.get_user(current_user, session, user_id)


@router.get("/", response_model=list[schemas.UserCreateResponse])
async def get_users(current_user = Depends(dependencies.role_checker([um.RoleEnum.SUPER_ADMIN])),
                     session: AsyncSession = Depends(get_db)):
    return await service.get_users(current_user, session)


# @router.post("/verify/{user_id}", response_model=schemas.UserCreateResponse)
# async def verufy(user_id: int, current_user: um.user = Depends(dependencies.role_checker(*roles)))