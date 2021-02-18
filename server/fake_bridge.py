import torch
import asyncio
import websockets
import pickle
import os, sys

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from utils.utils import receive_large_obj_over_ws


class FakeBridge:
    
    def __init__(self, server_uri="ws://localhost:8889"):
        self.server_uri = server_uri
        self.__sleeping_time = 3
        
    async def __check_connection(self):
        while True:
            try:
                if self.websocket is not None:
                    return self.websocket
            except AttributeError:
                await asyncio.sleep(self.__sleeping_time)

    async def receive_weights(self):
        async with websockets.connect(self.server_uri) as websocket:
            self.websocket = websocket
            while True:
                weights = await receive_large_obj_over_ws(self.websocket)
                print(f"[Bridge]: --> received {len(weights)} bytes")
                weights = pickle.loads(weights)
                print(f"[Bridge]: --> received {type(weights)}")

    async def send_features_vector(self, features_vector, label):
        await self.__check_connection()
        features_vector = features_vector.squeeze(0)
        features_vector = pickle.dumps(features_vector)
        await self.websocket.send((features_vector, label.to_bytes(1, 'little')))
        print(f"[Bridge]: --> sent features vector to server")
