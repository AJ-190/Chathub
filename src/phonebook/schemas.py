from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class CreateContact(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        
        if not any(p.isdigit() for p in value):
            raise ValueError("Password must contain digits only")
            
        return value
    
class CreateContactResponse(BaseModel):
    contact_id: int
    name: str
    phone: str
    email: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    
class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not value:
            return
        if not any(p.isdigit() for p in value):
            raise ValueError("Password must contain digits only")
        return value
    