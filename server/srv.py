import websockets
import asyncio
import torch
import pickle
import os, sys
from datetime import datetime
import os, sys
import logging

if __name__ == '__main__':
    sys.path.append(os.getcwd())
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from server.db_models import VggFeaturesVector
from server.db_manager import Session, engine, Base
from utils.utils import send_large_obj_over_ws, receive_large_obj_over_ws, create_file


def ws_client_disconnection_handler(func, *args, **kwargs):
    async def wrapper(*args, **kwargs):
        ws = args[1]
        try:
            return await func(*args, **kwargs)
        except websockets.exceptions.ConnectionClosedError as e:
            logging.info(f'[Server] --> clent {ws.remote_address} has disconnected')
    return wrapper

        
class Server:
    
    def __init__(self, address='localhost', model_port=8888, bridge_port=8889, sleep_time=3600):
        self.session = self.__db_up_()
        self.address = address
        self.model_port = model_port
        self.bridge_port = bridge_port
        self.sleep_time = sleep_time
        self._filename = 'server/new_weights.pth'
        if create_file(self._filename):
            logging.info('[Server] --> created local file \'new_weights.pth\'')
        self._last_weights_update_time = self.__get_last_weights_update_time()

    def __start(self):
        loop = asyncio.new_event_loop()
        done_tasks = loop.run_until_complete(asyncio.wait((
            websockets.serve(self.model_handler, self.address, self.model_port, loop=loop), 
            websockets.serve(self.bridge_handler, self.address, self.bridge_port, loop=loop)
        ), loop=loop))[0]
        self.websocket_connections = [task.result().websockets for task in done_tasks]
        loop.run_forever()
    
    def start(self, standalone=True):
        from threading import Thread
        t = Thread(target=self.__start, name='server')
        t.start()    

    def __db_up_(self):
        Base.metadata.create_all(engine)
        return Session()

    def db_upload(self, sample, label):
        obj = VggFeaturesVector(data=sample, label=label, timestamp=datetime.now())
        from uuid import uuid4
        self.session.add(obj)
        self.session.commit()

    def __get_last_weights_update_time(self):
        return datetime.fromtimestamp(os.path.getmtime(self._filename))

    @ws_client_disconnection_handler
    async def model_handler(self, websocket, path):
        last_sent_samples = set()
        while True:
            target_time = datetime.strptime(await websocket.recv(), "%Y-%m-%d %H:%M:%S")                                        # TODO: remove datetime.strptime(...)
            query = self.session.query(VggFeaturesVector) \
                .filter(VggFeaturesVector.timestamp >= target_time) \
                .filter(~VggFeaturesVector.id.in_(last_sent_samples)) \
                .all()
            result = [(q.features_vector, q.label) for q in query]
            last_sent_samples = {q.id for q in query} if query else last_sent_samples
            result = pickle.dumps(result)
            await send_large_obj_over_ws(websocket, result)
            if query:
                weights = await receive_large_obj_over_ws(websocket)
                logging.info(f"[Server] --> received {len(weights)} bytes")
                weights = pickle.loads(weights)
                logging.info(f"[Server] --> received {type(weights)}")
                torch.save(weights, self._filename)
                self._last_weights_update = datetime.now()

    @ws_client_disconnection_handler
    async def __listen_to_bridge(self, websocket, path):
        while True:
            sample_label_pair = await websocket.recv()
            sample = sample_label_pair[:len(sample_label_pair) -1]
            label = int.from_bytes(sample_label_pair[-1:], 'little')
            self.db_upload(sample, label)
            sample = pickle.loads(sample)
            logging.info(f"[Server] --> received features vector with shape {sample.shape} and label {label} from bridge and saved to db")

    @ws_client_disconnection_handler
    async def __send_to_bridge(self, websocket, path):
        while True:
            new_last_weights_update_time = self.__get_last_weights_update_time()
            if self._last_weights_update_time < new_last_weights_update_time:
                weights = torch.load(self._filename)
                weights = pickle.dumps(weights)
                await send_large_obj_over_ws(websocket, weights)
                self._last_weights_update_time = datetime.now()
            # TODO: replace with self.sleep_time
            await asyncio.sleep(5)                              

    async def bridge_handler(self, websocket, path):
        t1 = asyncio.create_task(self.__listen_to_bridge(websocket, path))
        t2 = asyncio.create_task(self.__send_to_bridge(websocket, path))
        await asyncio.gather(t1, t2)
                

if __name__ == '__main__':
    server = Server()
    server.start()
