from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter


router = APIRouter(tags=['Websocket'])

class ConnectionManager:
    
    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = {}
        
    async def connect(self, user_id: int, websocket: WebSocket):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
    async def disconnect(self, user_id: int, websocket: WebSocket):
        connections = self.active_connections.get(user_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self.active_connections.pop(user_id, None)
        
    async def send_personal_message(self, user_id: int, message: str):
        connections = self.active_connections.get(user_id)
        if not connections:
            return False
        for connection in connections:
            await connection.send_text(message)
        return True

manager = ConnectionManager()

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, user_id: int = 0):
    await websocket.accept()
    await manager.connect(user_id, websocket)
    try:
        while True:
            
           data =  await websocket.receive_text()
           await manager.send_personal_message(user_id, data)
    except WebSocketDisconnect:
         await manager.disconnect(user_id, websocket)