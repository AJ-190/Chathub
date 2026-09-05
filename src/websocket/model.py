from src.db.database import get_db, Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func
from datetime import datetime

class Chat(Base):
    
    __tablename__ = "chat"
    chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    reciever_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)
    is_read: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("Users", back_populates="sent_chats", foreign_keys=[sender_id])
    receiver = relationship("Users", back_populates="received_chats", foreign_keys=[reciever_id])
    