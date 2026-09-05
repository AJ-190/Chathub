from sqlalchemy.ext.asyncio import AsyncSession
from src.users import model as um
from src.phonebook import schemas, model as pm
from fastapi import HTTPException, status
from sqlalchemy import select, or_



async def add_contact(credentials: schemas.CreateContact,
                      session: AsyncSession,
                      current_user: um.Users):
    exist = (
        await session.execute(
            select(pm.Contacts)
            .where(pm.Contacts.phone == credentials.phone)
            .where(pm.Contacts.user_id == current_user.user_id)
        )
    ).scalar_one_or_none()
    
    if exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact already exist")
    contact = pm.Contacts(**credentials.model_dump(), user_id=current_user.user_id)
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact



async def get_contact(contact_id: int, session: AsyncSession, current_user: um.Users):
    contact = (
        await session.execute(
            select(
                pm.Contacts
            ).where(pm.Contacts.user_id == current_user.user_id)
            .where(pm.Contacts.contact_id == contact_id)
        )
    ).scalar_one_or_none()
    
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


async def get_contacts(current_user: um.Users, session: AsyncSession, search: str, limit: int, skip: int):
    contacts = (

            select(pm.Contacts)
            .where(pm.Contacts.user_id == current_user.user_id)
            

    )
    ex_contacts = (await session.execute(contacts)).scalars().all()
    
    if not ex_contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found")
    
    if search:
        base_search = f"%{search}%"
        
        contacts = contacts.where(
            or_(
                pm.Contacts.name.ilike(base_search),
                pm.Contacts.phone.ilike(base_search),
                pm.Contacts.email.ilike(base_search)
                
            )
        )
        
    
        
    searched_contacts = (await session.execute(contacts.order_by(pm.Contacts.created_at).limit(limit).offset(skip))).scalars().all()
    if not searched_contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    
    return searched_contacts
    
async def update_contact(post: schemas.ContactUpdate, contact_id: int, current_user: um.Users, session:AsyncSession):
    contact: pm.Contacts = await get_contact(contact_id, session, current_user )
    
    user=  (
        await session.execute(
            select(pm.Contacts)
            .where(pm.Contacts.phone == post.phone)
            .where(pm.Contacts.user_id == current_user.user_id)
        )
    ).scalar_one_or_none()
    
    if user and user.phone != post.phone:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact with the number already exist")
    
    for key, value in post.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
        
    await session.commit()
    await session.refresh(contact)
    return contact


async def delete_contact(contact_id: int, session: AsyncSession, current_user: um.Users):
    contact = (
        await session.execute(
            select(pm.Contacts)
            .where(pm.Contacts.user_id == current_user.user_id)
            .where(pm.Contacts.contact_id == contact_id)
            
        )
    ).scalar_one_or_none()
    
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    session.delete(contact)
    await session.commit()
    return 
    

        
        