import serial
from time import sleep
import torch
import asyncio
import websockets
import pickle
import os, sys
import cv2

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from utils.utils import receive_large_obj_over_ws
from model.masked_face_vgg import MaskedFaceVgg
from torchvision import transforms

class Bridge():
    def __init__(self, server_uri="ws://localhost:8889"):
        self.arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.5)
        self.server_uri = server_uri
        self.__sleeping_time = 3
        self.model = MaskedFaceVgg()
        self.__camera = 1
        self.cam = cv2.VideoCapture(0)
        sleep(2)      

    async def __check_connection(self):
        while True:
            try:
                if self.websocket is not None:
                    return self.websocket
            except AttributeError:
                await asyncio.sleep(self.__sleeping_time)

    async def receive_weights(self):
        while True:
            try:
                async with websockets.connect(self.server_uri) as websocket:
                    print('BRIDGE CONNECTED')
                    self.websocket = websocket
                    while True:
                        weights = await receive_large_obj_over_ws(self.websocket)
                        print(f"[Bridge]: --> received {len(weights)} bytes")
                        weights = pickle.loads(weights)
                        self.model.classifier.load_state_dict(weights, strict=True)
                        print(f"[Bridge]: --> weights loading completed")
            except ConnectionRefusedError:
                await asyncio.sleep(3)

    async def send_features_vector(self, features_vector, label):
        await self.__check_connection()
        features_vector = features_vector.squeeze(0)
        features_vector = pickle.dumps(features_vector)
        await self.websocket.send((features_vector, label.to_bytes(1, 'little')))
        print(f"[Bridge]: --> sent features vector to server")
    
    def take_picture(self, label=None):
        go = input('Press enter to take a pick...')
        cam.open(CAMERA)
        ret, frame = cam.read()
        cam.release()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = transforms.functional.to_tensor(frame)
        img = img.unsqueeze(0)
        img = torch.nn.functional.interpolate(img, size=(224, 224))
        result = None
        with torch.no_grad():
            if label:
                result = self.model.get_feature_vector(img)
                asyncio.create_task(self.send_features_vector(result, label))
            else:
                predicitons = self.model(img)
                result = torch.argmax(predictions, 1).squeeze(0)
                print(f"Label: {'CORRECT' if result.item() == 1 else 'INCORRECT'}")
        return result          

    def open(self):
        self.arduino.open()

    def close(self):
        self.arduino.close()

    def turn_on(self, device):
        if device == 'correct': 
            self.arduino.write(bytes(b'\xff'))
            self.arduino.write(bytes(b'\x01'))
            self.arduino.write(bytes(b'\x01'))
            self.arduino.write(bytes(b'\xfe'))
            sleep(0.5)
            self.read()
            sleep(4)
            self.arduino.write(bytes(b'\xff'))
            self.arduino.write(bytes(b'\x01'))
            self.arduino.write(bytes(b'\xfe'))
            sleep(0.5)
            self.read()
            sleep(0.5)
        if device == 'incorrect': 
            self.arduino.write(bytes(b'\xff'))
            self.arduino.write(bytes(b'\x02'))
            self.arduino.write(bytes(b'\x01'))
            self.arduino.write(bytes(b'\xfe'))
            sleep(0.5)
            self.read()
            sleep(4)
            self.arduino.write(bytes(b'\xff'))
            self.arduino.write(bytes(b'\x02'))
            self.arduino.write(bytes(b'\xfe'))
            sleep(0.5)
            self.read()
            sleep(0.5)

    #TODO remove read fuction (just for debugging)
    def read(self):
        data = self.arduino.readline().decode('ascii')
        print(data)

    def read_msg(self,msg):
        if msg[0]!=b'\xff':
            return 0
        if msg[1]!=b'\x03':
            return 0
        if msg[2]==b'\x01':
            return 1
        elif msg[2]==b'\x02':
            return 2


    def is_waiting(self):
        return True

    def loop(self):
        msg=[]
        while True:
            if self.is_waiting():
                self.turn_on('incorrect')
            else:
                if self.arduino.in_waiting>0:
                    recieved = self.arduino.read(1)
                    if recieved==b'\xfe':
                        if len(msg)!=3:
                            msg=[]
                        else:
                            response = self.read_msg(msg)
                            if response!=0:
                                if response==1:
                                    print('taking a picture')
                                if response==2:
                                    print('retrainig')
                            msg=[]
                    else:
                        msg.append(recieved)
    
    def start(self):
        self.loop()
        asyncio.get_event_loop().run_until_complete(self.receive_weights())
        asyncio.get_event_loop().run_forever()
        self.close()


if __name__ == '__main__':
    br = Bridge()
    br.start()
