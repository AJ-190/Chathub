from fastapi import APIRouter, Depends, HTTPException
from src.auth import schemas
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import service as auth_service
from src.users import model as um
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from src.auth import dependencies

router = APIRouter(prefix="/auth", tags=['Authentication'])

@router.post("/sign_up", response_model=schemas.UserCreateResponse)
async def sign_up(credentials: schemas.UserCreateAccount,
                  session: AsyncSession = Depends(get_db)):
    return await auth_service.sign_up(credentials, session)


@router.post("/login", response_model=schemas.TokenReponse)
async def login(credentials: OAuth2PasswordRequestForm = Depends(), 
                session: AsyncSession = Depends(get_db)):
    return await auth_service.login(credentials, session)

