from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect
from src.users import model as um
from sqlalchemy import select, or_, and_, func
from src.chat import dependencies as dps, model as cm, schemas as cs
from src.websocket.manager import ConnectionManager
from src.auth import dependencies as auth_deps
import json
from datetime import datetime
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
            data = json.loads(raw)
            
            recipient_id = int(data['to'])
            body = data['body']
            
            message = await save_message(session,current_user.user_id, recipient_id, body)

            outgoing_msg = {
                "from": current_user.user_id,
                "to": recipient_id,
                "message": body,
                "body": body,
                "sent_at": message.created_at.isoformat()
            }
            
            delivered_live = await manager.send_personal_message(recipient_id, json.dumps({**outgoing_msg}))
            await websocket.send_json({**outgoing_msg,  "self": True})
        except WebSocketDisconnect:
            await manager.disconnect(current_user.user_id, websocket)
            break
        except Exception:
            await manager.disconnect(current_user.user_id, websocket)
            await websocket.close()
            break
            
async def save_message(session: AsyncSession, sender_id, reciever_id, body):
    message = um.Chat(sender_id=sender_id, reciever_id=reciever_id, message=body)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

@router.get("/conversations/{other_user_id}/messages")
async def get_conversations(other_user_id: int,
                            session: AsyncSession = Depends(get_db),
                            current_user: um.Users = Depends(auth_deps.role_checker([*roles]))):
    
    messages = (

            select(cm.Chat)
            .where(
                ((cm.Chat.sender_id == other_user_id) & (cm.Chat.reciever_id == current_user.user_id)) 
                |  ((cm.Chat.sender_id == current_user.user_id) & (cm.Chat.reciever_id == other_user_id))
                )
    )
    
    message =( await session.execute(messages.order_by(cm.Chat.created_at.desc()))).scalars().all()
    return message


@router.get("/conversations", response_model=list[cs.ConversationSummary])
async def get_conversation_list(search: str | None = None,
                                session: AsyncSession = Depends(get_db),
                                current_user: um.Users = Depends(auth_deps.role_checker([*roles]))):
    me = current_user.user_id

    involved = await session.execute(
        select(cm.Chat.sender_id, cm.Chat.reciever_id)
        .where(or_(cm.Chat.sender_id == me, cm.Chat.reciever_id == me))
    )
    other_ids = {
        other
        for sender_id, reciever_id in involved.all()
        if (other := sender_id if sender_id != me else reciever_id) != me
    }

    if not other_ids:
        return []

    users = await session.execute(select(um.Users).where(um.Users.user_id.in_(other_ids)))
    user_map = {u.user_id: u for u in users.scalars().all()}

    needle = search.strip().lower() if search else ""

    results = []
    for other_id, u in user_map.items():
        if needle and needle not in u.name.lower() and needle not in u.phone.lower():
            continue

        last = (
            await session.execute(
                select(cm.Chat)
                .where(
                    or_(
                        and_(cm.Chat.sender_id == me, cm.Chat.reciever_id == other_id),
                        and_(cm.Chat.sender_id == other_id, cm.Chat.reciever_id == me),
                    )
                )
                .order_by(cm.Chat.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        unread = (
            await session.execute(
                select(func.count())
                .select_from(cm.Chat)
                .where(
                    cm.Chat.sender_id == other_id,
                    cm.Chat.reciever_id == me,
                    cm.Chat.is_read == False,
                )
            )
        ).scalar_one()

        results.append(
            cs.ConversationSummary(
                user=cs.ChatUserInfo(
                    user_id=u.user_id,
                    name=u.name,
                    phone=u.phone,
                    email=u.email,
                ),
                last_message=last.message if last else None,
                last_message_at=last.created_at.isoformat() if last else None,
                unread=unread,
            )
        )

    results.sort(
        key=lambda r: r.last_message_at or datetime.min,
        reverse=True,
    )
    return results


@router.get("/presence", response_model=cs.PresenceResponse)
async def get_presence(current_user: um.Users = Depends(auth_deps.role_checker([*roles]))):
    return {"online": list(manager.get_online_ids())}