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

    async def bridge_handler(self, websocket, path):
        pass
