from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import select
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, APIRouter


router = APIRouter(tags=['Websocket'])

class ConnectionManager:
    
    def __init__(self):
        self.active_connections: list = []
        
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if websocket in self.active_connections:
            return
        self.active_connections.append(websocket)
        
    async def disconnect(self, websocket: WebSocket):
        if websocket not in self.active_connections:
            return 
        self.active_connections.remove(websocket)
        
    async def send_personal_message(self, websocket: WebSocket, message):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            await self.disconnect(websocket)

manager = ConnectionManager()

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            
           data =  await websocket.receive_text()
           await manager.send_personal_message(websocket, data)
    except WebSocketDisconnect:
         await manager.disconnect(websocket)