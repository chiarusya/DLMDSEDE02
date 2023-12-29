import asyncio
import websockets
import nest_asyncio

nest_asyncio.apply()

async def listen():
    url = "ws://localhost:6790"
    async with websockets.connect(url) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")

asyncio.get_event_loop().run_until_complete(listen())
