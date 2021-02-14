import websockets
import asyncio
import torch
import pickle
from datetime import datetime
from db_models import VggFeaturesVector
from db_manager import Session, engine, Base


class Server:
    
    def __init__(self, address='localhost', model_port=8888, bridge_port=8889):
        self.session = self.__db_up_()
        self.address = address
        self.model_port = model_port
        self.bridge_port = bridge_port

    def start(self):
        return websockets.serve(self.model_handler, self.address, self.model_port), websockets.serve(self.bridge_handler, self.address, self.bridge_port)

    def __db_up_(self):
        Base.metadata.create_all(engine)
        return Session()

    async def model_handler(self, websocket, path):
        while True:
            target_time = datetime.strptime(await websocket.recv(), "%Y-%m-%d %H:%M:%S")                                        # TODO: remove datetime.strptime(...)
            query = self.session.query(VggFeaturesVector).filter(VggFeaturesVector.timestamp >= target_time).limit(10).all()
            result = [(q.features_vector, q.label) for q in query]
            await websocket.send(pickle.dumps(result))

            weights_size = int.from_bytes(await websocket.recv(), 'little')
            current_received_size = 0
            l = {}
            while current_received_size != weights_size:
                chunk = await websocket.recv()
                index = int.from_bytes(chunk[-4:], 'little')
                l[index] = chunk[:len(chunk)- 4]
                current_received_size += len(l[index])
            print(f"[Server] --> received {sum((len(x) for x in l.values()))} bytes")
            sorted_indexes = sorted(l.keys())
            obj = b''.join([l[i] for i in sorted_indexes])
            weights = pickle.loads(obj)
            from model.models import MaskedFaceVgg
            model = MaskedFaceVgg()
            model.classifier.load_state_dict(weights)
            print(type(weights))
            torch.save(weights, 'server/new_weights.pth')
            print(f"[Server] --> weights loading completed")

    async def bridge_handler(self, websocket, path):
        pass
