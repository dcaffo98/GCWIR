import asyncio
import websockets
import torch
import torch.nn as nn
import pickle
import numpy as np
from datetime import datetime
from model.models import MaskedFaceVgg
from utils.utils import send_large_obj_over_ws

class Client:

    def __init__(self, server_uri="ws://localhost:8888", polling_interval=3600):
        self.server_uri = server_uri
        self.polling_interval = polling_interval
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        self.model = MaskedFaceVgg().to(self.device)
        self.optimizer = torch.optim.SGD(self.model.classifier.parameters(), lr=0.001, momentum=0.9)
        self.cross_entropy = nn.CrossEntropyLoss()

    async def request_samples(self):
        while True:
            async with websockets.connect(self.server_uri) as websocket:
                await websocket.send(str(datetime(2021, 2, 10)))                    # TODO: replace with datetime.now()
                response = pickle.loads(await websocket.recv())
                samples = torch.stack([sample for sample, _ in response], dim=0).to(self.device)
                labels = torch.from_numpy(np.fromiter((label for _, label in response), int)).to(self.device)
                print(f"[Client] --> recevied: {samples.shape}, {labels.shape}")
                predictions = self.model.classify(samples)
                loss = self.cross_entropy(predictions, labels)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                classifier = pickle.dumps(self.model.classifier.state_dict())
                import time
                start = time.time()
                await websocket.send(len(classifier).to_bytes(16, 'little'))
                await send_large_obj_over_ws(websocket, classifier, chunk_size=1000000)
                print(f"ELAPSED TIME: {time.time() - start}")
                print(f"[Client] --> sent {len(classifier)} bytes")
                print('[Client] --> training completed!')
                await asyncio.sleep(self.polling_interval)            
