from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func, Enum as SAEnum, false
from datetime import datetime
import enum
from src.db.database import Base


class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    USER = "user"


def enum_values(enum_cls):
    return [member.value for member in enum_cls]



class Users(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=True, unique=True)
    role: Mapped[SAEnum] = mapped_column(SAEnum(RoleEnum, values_callable=enum_values), default=RoleEnum.USER, server_default=RoleEnum.USER.value, nullable=False)
    is_verified: Mapped[bool] = mapped_column(nullable=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    
    contact = relationship("Contacts", back_populates="user", passive_deletes=True)
    sent_chats = relationship("Chat", back_populates="sender", foreign_keys="Chat.sender_id", passive_deletes=True)
    received_chats = relationship("Chat", back_populates="receiver", foreign_keys="Chat.reciever_id", passive_deletes=True)


from src.chat.model import Chat