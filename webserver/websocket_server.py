import asyncio
import websockets
import json
from aiohttp import web

connected_clients = set()

async def register_client(websocket):
    connected_clients.add(websocket)

async def unregister_client(websocket):
    connected_clients.remove(websocket)

async def websocket_handler(websocket, path):
    await register_client(websocket)
    try:
        async for message in websocket:
            pass
    finally:
        await unregister_client(websocket)

async def http_handler(request):
    data = await request.json()
    for ws in connected_clients:
        await ws.send(json.dumps(data))
    return web.Response()

app = web.Application()
app.add_routes([web.post('/broadcast', http_handler)])
app_runner = web.AppRunner(app)

async def main():
    await app_runner.setup()
    web_server = web.TCPSite(app_runner, '0.0.0.0', 8080)
    await web_server.start()
    ws_server = await websockets.serve(websocket_handler, '0.0.0.0', 6789)
    await asyncio.Future()  # run forever

asyncio.run(main())
