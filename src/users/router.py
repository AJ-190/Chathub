from fastapi import APIRouter, Depends
from src.users import service as service, model as um, schemas as um_schemas
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import schemas ,dependencies
from src.db.database import get_db

roles = {um.RoleEnum.USER, um.RoleEnum.SUPER_ADMIN}
router = APIRouter(prefix="/users", tags=['Users'])

@router.get("/get/user/{user_id}", response_model=schemas.UserCreateResponse)
async def get_user(user_id: int, current_user: um.Users = Depends(dependencies.role_checker([um.RoleEnum.SUPER_ADMIN, um.RoleEnum.USER])) , 
                   session: AsyncSession = Depends(get_db)):
    
    return await service.get_user(current_user, session, user_id)


@router.get("/", response_model=list[schemas.UserCreateResponse])
async def get_users(current_user = Depends(dependencies.role_checker([*roles])),
                     session: AsyncSession = Depends(get_db)):
    return await service.get_users(current_user, session)


@router.put("/{user_id}", response_model=schemas.UserCreateResponse)
async def update_user(credentials: um_schemas.UserUpdate,
                      user_id: int
                      ,current_user = Depends(dependencies.role_checker([*roles])),
                      session = Depends(get_db)):
    return await  service.update_user(credentials, user_id, current_user, session)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, 
                      current_user = Depends(dependencies.role_checker(*roles)),
                      session = Depends(get_db)):
    return  await service.delete_user(user_id, current_user, session)