import asyncio


async def send_large_obj_over_ws(websocket, obj, chunk_size=1000000):
    current = 0
    tasks = set()
    while current <= len(obj):
        chunk = obj[current:current + chunk_size]
        tasks.add(asyncio.create_task(websocket.send((chunk, current.to_bytes(4, 'little')))))
        current += chunk_size
    await asyncio.wait(tasks)
