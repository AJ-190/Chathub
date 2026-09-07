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
    token= ""
    uri = f"ws://localhost:8000/chat/ws/chat?token={token}"
    async with websockets.connect(uri) as ws:
        # Send a message
        msg = json.dumps({"to": 5, "body": "Hello!"})
        await ws.send(msg)
        
        # Listen for responses
        response = await ws.recv()
        print(response)

asyncio.run(test())