import asyncio
from uuid import uuid4
import os, sys
import logging

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

def stringify_uuid4():
    return str(uuid4())

async def send_large_obj_over_ws(websocket, obj, chunk_size=1000000):
    await websocket.send(len(obj).to_bytes(16, 'little'))
    current = 0
    tasks = set()
    while current <= len(obj):
        chunk = obj[current:current + chunk_size]
        tasks.add(asyncio.create_task(websocket.send((chunk, current.to_bytes(4, 'little')))))
        current += chunk_size
    await asyncio.wait(tasks)

async def receive_large_obj_over_ws(websocket):
    size = int.from_bytes(await websocket.recv(), 'little')
    current_received_size = 0
    l = {}
    while current_received_size != size:
        chunk = await websocket.recv()
        index = int.from_bytes(chunk[-4:], 'little')
        l[index] = chunk[:len(chunk)- 4]
        current_received_size += len(l[index])
    sorted_indexes = sorted(l.keys())
    return b''.join([l[i] for i in sorted_indexes])

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')    

def create_file(path):
    if os.path.exists(path):
        return False
    else:
        open(path, 'wb').close()
        return os.path.exists(path)
