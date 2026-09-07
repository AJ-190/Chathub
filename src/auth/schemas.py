from pydantic import BaseModel, ConfigDict, field_validator, SecretStr
from typing import Optional
from datetime import datetime
class UserCreateAccount(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    password: SecretStr
    
    @field_validator("password")
    @classmethod
    def validate(cls, value):
        if value is None:
            return None
        pw = value.get_secret_value() if isinstance(value, SecretStr) else value
        
        if len(pw) < 8:
            raise ValueError("password length must be equal to or greater than 8")
        if not any(p.isdigit() for p in pw):
            raise ValueError("password must contain at least one digit")
        if not any(p.isupper() for p in pw):
            raise ValueError("Password muat contain at least one uppercase letter")
        if not any(p.islower() for p in pw):
            raise ValueError("Password must contain at least one lowercase letter")
        return value
    
    
class UserCreateResponse(BaseModel):
    user_id: int
    name: str
    phone: str
    role: str
    is_verified: bool
    email: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    
    
class Login(BaseModel):
    phone: str
    email: Optional[str] = None
    password: SecretStr
    
class TokenReponse(BaseModel):
    refresh_token: str
    access_token: str
    type: str
    
    model_config = ConfigDict(from_attributes=True)