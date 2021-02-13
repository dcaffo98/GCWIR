import asyncio
import websockets
import torch
import pickle
import numpy as np
from datetime import datetime


class Client:

    def __init__(self, server_uri="ws://localhost:8888", polling_interval=3600):
        self.server_uri = server_uri
        self.polling_interval = polling_interval

    async def request_samples(self):
        while True:
            async with websockets.connect(self.server_uri) as websocket:
                await websocket.send(str(datetime(2021, 2, 10)))                    # TODO: replace with datetime.now()
                response = pickle.loads(await websocket.recv())
                samples = torch.stack([sample for sample, _ in response], dim=0)
                labels = torch.from_numpy(np.fromiter((label for _, label in response), int))
                print(samples.shape, labels.shape)
                await asyncio.sleep(self.polling_interval)
            
