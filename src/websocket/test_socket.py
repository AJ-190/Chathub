import websockets
import asyncio




async def websocket():
    async with websockets.connect("ws://localhost:8000/ws/") as conn:
        await conn.send("Hey, how are you doinng")
        response = await conn.recv()
        print(response)
        
asyncio.run(websocket())