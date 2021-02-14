import asyncio
from threading import Lock


lock = Lock()

async def send_large_obj_over_ws(websocket, obj, chunk_size=1000000):
    global current
    current = 0
    async def _():
        global current
        while current <= len(obj):
            with lock:
                chunk = obj[current:current + chunk_size]
                asyncio.create_task(websocket.send((chunk, current.to_bytes(4, 'little'))))
                #asyncio.run_coroutine_threadsafe(websocket.send((chunk, current.to_bytes(4, 'little'))), asyncio.get_event_loop())
                current += chunk_size
    asyncio.create_task(_())