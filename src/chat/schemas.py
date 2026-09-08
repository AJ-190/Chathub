from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ChatUserInfo(BaseModel):
    user_id: int
    name: str
    phone: str
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationSummary(BaseModel):
    user: ChatUserInfo
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread: int = 0


class PresenceResponse(BaseModel):
    online: list[int]