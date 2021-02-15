import websockets
import asyncio
import torch
import pickle
import os
from datetime import datetime
from db_models import VggFeaturesVector
from db_manager import Session, engine, Base
from utils.utils import send_large_obj_over_ws, receive_large_obj_over_ws


class Server:
    
    def __init__(self, address='localhost', model_port=8888, bridge_port=8889, sleep_time=3600):
        self.session = self.__db_up_()
        self.address = address
        self.model_port = model_port
        self.bridge_port = bridge_port
        self.sleep_time = sleep_time
        self._filename = 'server/new_weights.pth'
        self._last_weights_update_time = self.__get_last_weights_update_time()
        if not os.path.exists(self._filename):
            os.mknod(self._filename)
            print(10)

    def start(self):
        return websockets.serve(self.model_handler, self.address, self.model_port), websockets.serve(self.bridge_handler, self.address, self.bridge_port)

    def __db_up_(self):
        Base.metadata.create_all(engine)
        return Session()

    def db_upload(self, sample, label):
        obj = VggFeaturesVector(data=sample, label=label)
        self.session.add(obj)
        self.session.commit()

    def __get_last_weights_update_time(self):
        return datetime.fromtimestamp(os.path.getmtime(self._filename))

    async def model_handler(self, websocket, path):
        while True:
            target_time = datetime.strptime(await websocket.recv(), "%Y-%m-%d %H:%M:%S")                                        # TODO: remove datetime.strptime(...)
            query = self.session.query(VggFeaturesVector).filter(VggFeaturesVector.timestamp >= target_time).limit(10).all()
            result = [(q.features_vector, q.label) for q in query]
            await websocket.send(pickle.dumps(result))
            weights = await receive_large_obj_over_ws(websocket)
            print(f"[Server] --> received {len(weights)} bytes")
            weights = pickle.loads(weights)
            from model.models import MaskedFaceVgg
            model = MaskedFaceVgg()
            model.classifier.load_state_dict(weights)
            print(type(weights))
            torch.save(weights, self._filename)
            self._last_weights_update = datetime.now()
            print(f"[Server] --> weights loading completed")
            del model

    async def __listen_to_bridge(self, websocket, path):
        while True:
            sample_label_pair = await websocket.recv()
            sample = sample_label_pair[:len(sample_label_pair) -1]
            label = int.from_byte(sample_label_pair[-4:], 'little')
            self.db_upload(sample, label)

    async def __send_to_bridge(self, websocket, path):
        while True:
            new_last_weights_update_time = self.__get_last_weights_update_time()
            if self._last_weights_update_time < new_last_weights_update_time:
                weights = torch.load(self._filename)
                weights = pickle.dumps(weights)
                await send_large_obj_over_ws(websocket, weights)
                self._last_weights_update_time = datetime.now()
            await asyncio.sleep(5)

    async def bridge_handler(self, websocket, path):
        t1 = asyncio.create_task(self.__listen_to_bridge(websocket, path))
        t2 = asyncio.create_task(self.__send_to_bridge(websocket, path))
        await asyncio.gather(t1, t2)
                