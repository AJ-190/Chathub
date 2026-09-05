from fastapi import APIRouter, status, HTTPException, Depends
from src.phonebook import schemas, model, service as pm_service
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.auth.dependencies import role_checker
from src.users import model as um

router = APIRouter(prefix="/phonebook", tags=['Phonebook'])

@router.post("/create_contact", response_model=schemas.CreateContactResponse, status_code=201)
async def add_contact(credentails: schemas.CreateContact,
                      session: AsyncSession = Depends(get_db),
                      current_user = Depends(role_checker([um.RoleEnum.SUPER_ADMIN, um.RoleEnum.USER]))):
    return await pm_service.add_contact(credentails, session, current_user)


@router.get("/contacts/{contact_id}", response_model=schemas.CreateContactResponse)
async def get_contact(contact_id: int,
                      session: AsyncSession = Depends(get_db),
                      current_user = Depends(role_checker([um.RoleEnum.USER, um.RoleEnum.SUPER_ADMIN]))):
    return await pm_service.get_contact(contact_id, session, current_user)

@router.get("/contacts", response_model=list[schemas.CreateContactResponse])
async def get_contacts(current_user = Depends(role_checker([um.RoleEnum.USER, um.RoleEnum.SUPER_ADMIN])),
                       session = Depends(get_db),
                       search: str = None, 
                       skip: int = None,
                       limti: int = None):
    return await pm_service.get_contacts(current_user, session, search, limti, skip)
@router.put("/contacts/{contact_id}", response_model=schemas.CreateContactResponse)
async def update_contact(post: schemas.ContactUpdate, 
                         contact_id: int, session: AsyncSession = Depends(get_db),
                         current_user = Depends(role_checker([um.RoleEnum.USER, um.RoleEnum.SUPER_ADMIN]))):
    return await pm_service.update_contact(post, contact_id, current_user, session)


@router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: int, 
                         session:AsyncSession = Depends(get_db),
                         current_user = Depends(role_checker([um.RoleEnum.USER, um.RoleEnum.SUPER_ADMIN]))):
    return await pm_service.delete_contact(contact_id, session, current_user)