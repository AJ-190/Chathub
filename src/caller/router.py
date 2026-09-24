import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from websocket.manager import ConnectionManager
from caller.call_manager import CallManager


router = APIRouter(prefix="/call", tags=["Caller"])
manager = ConnectionManager()
calls = CallManager()

CALL_TIME_SECONDS = 25


async def start_call_timeout(call_id: str):
    await asyncio.sleep(CALL_TIME_SECONDS)
    
    call = calls.get_call(call_id)
    if call is None:
        return
    
    calls.end_call(call_id)
    await manager.send_personal_message(call.caller_id,{
        "type": "call:timeout",
        "call_id": call_id,
    })
    
    await manager.send_personal_message(call.callee_id, {
        "type": "call:missed",
        "call_id": call_id,
        "from": call.caller_id,
    })
    
    
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id,websocket)
    
    try:
        
        while True:
            message: dict = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "call:invite":
                await handle_invite(user_id,message)
    except Exception:
        await manager.disconnect(user_id, websocket)
        
        
async def handle_invite(caller_id: int, message: dict):
    callee_id = message['to']
    
    if not manager.is_online(callee_id):
        await manager.send_personal_message(caller_id, {
            "type": "call:unavailable",
            "to": callee_id
        })
        return
    
    call = calls.create_call(caller_id, callee_id)
    call.timeout_task = asyncio.create_task(start_call_timeout(call.call_id))
    
    await manager.send_personal_message(callee_id, {
        "type": "call:incoming",
        "call_id": call.call_id
    })

    await manager.send_personal_message(caller_id, {
        "type": "call:ringing",
        "call_id": call.call_id,
        "to": callee_id
    })
    

async def handle_accept(user_id: int, message: dict):
    call_id = message['call_id']
    call = calls.get_call(call_id)
    if call is None or call.callee_id != user_id:
        return
    
    calls.end_call(call_id)
    await manager.send_personal_message(call.caller_id, {
        "type": "call.accepted",
        "call_id": call_id,
        "by": user_id
    })
   