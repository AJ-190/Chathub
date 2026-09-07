import websockets
import asyncio




# async def websocket():
#     async with websockets.connect("ws://localhost:8000/ws/") as conn:
#         await conn.send("Hey, how are you ")
#         response = await conn.recv()
#         print(response)
        
# asyncio.run(websocket())





import json

async def test():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7InVzZXJfaWQiOjEsInJvbGUiOiJzdXBlcl9hZG1pbiJ9LCJqdGkiOiI4NjBkYmM0Ny0wZDIzLTRjZGItYjcxMi05MTZkMGM2NDk3MGYiLCJleHAiOjE3ODg3NTUxNTIsInJlZnJlc2giOmZhbHNlfQ.Qtr5XS5ADe_K9pvzhMzFoEi_KV29anzbzrZeb-025qE"
    uri = f"ws://localhost:8000/chat/ws/chat?token={token}"
    async with websockets.connect(uri) as ws:
        # Send a message
        msg = json.dumps({"to": 5, "body": "Hello!"})
        await ws.send(msg)
        
        # Listen for responses
        response = await ws.recv()
        print(response)

asyncio.run(test())