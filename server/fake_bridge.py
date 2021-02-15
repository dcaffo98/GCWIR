import torch
import asyncio
import websockets
import pickle
from utils.utils import receive_large_obj_over_ws


class FakeBridge:
    
    def __init__(self, server_uri="ws://localhost:8889"):
        self.server_uri = server_uri

    async def foo(self):
        async with websockets.connect(self.server_uri) as websocket:
            while True:
                weights = await receive_large_obj_over_ws(websocket)
                print(f"[Bridge]: --> received {len(weights)} bytes")
                weights = pickle.loads(weights)
