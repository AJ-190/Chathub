from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect
from src.users import model as um
from sqlalchemy import select
from src.chat import dependencies as dps, model as cm
from src.websocket.manager import ConnectionManager
import json
from src.db.database import get_db

manager = ConnectionManager()



roles = {um.RoleEnum.SUPER_ADMIN, um.RoleEnum.USER}
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.websocket("/ws/chat")
async def send_message(websocket: WebSocket,
                       current_user: um.Users = Depends(dps.role_checker([*roles])),
                       session: AsyncSession = Depends(get_db)):
    await websocket.accept()
    await manager.connect(current_user.user_id, websocket)
    
    while True:
        
        try:
            
            raw = await websocket.receive_text()
            data = json.load(raw)
            
            recipient_id = data['to']
            body = data['body']
            
            message = await save_message(session,current_user.user_id, recipient_id, body)

            outgoing_msg = {
                "from": current_user.user_id,
                "messae": body,
                "body": body,
                "sent_at": message.created_at.isoformat()
            }
            
            delivered_live = await manager.send_personal_message(recipient_id, {**outgoing_msg}, websocket)
            await websocket.send_json({**outgoing_msg,  "self": True})
        except WebSocketDisconnect:
            await manager.disconnect(current_user.user_id, websocket)
            
async def save_message(session: AsyncSession, sender_id, reciever_id, body):
    message = um.Chat(sender_id=sender_id, reciever_id=reciever_id, message=body)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

@router.get("/conversations/{other_user_id}/messages")
async def get_conversations(other_user_id: int,
                            session: AsyncSession = Depends(get_db),
                            current_user: um.Users = Depends(dps.role_checker([*roles]))):
    
    messages = (

            select(cm.Chat)
            .where(
                ((cm.Chat.sender_id == other_user_id) & (cm.Chat.reciever_id == current_user.user_id)) 
                |  ((cm.Chat.sender_id == other_user_id) & (cm.Chat.reciever_id == current_user.user_id)) 
                )
    )
    
    message =( await session.execute(messages.order_by(cm.Chat.created_at.desc()))).scalars().all()
    return message