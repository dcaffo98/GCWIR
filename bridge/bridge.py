from os import path
import serial
from time import sleep
import torch
import asyncio
import websockets
import pickle
import os, sys
import cv2
import serial.tools.list_ports
from threading import Thread, Event, Lock
import logging

if __name__ == '__main__':
    sys.path.append(os.getcwd())
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from utils.utils import receive_large_obj_over_ws, clear_screen
from model.masked_face_vgg import MaskedFaceVgg
from torchvision import transforms

class Bridge():
    def __init__(self, server_uri="ws://localhost:8889"):
        self.arduino = self.__get_serial_port(baudrate=115200, timeout=.5)
        self.server_uri = server_uri
        self.__sleeping_time = 3
        self.model = MaskedFaceVgg()
        self.__camera = 0
        self._cam = cv2.VideoCapture(self.__camera)
        self._label0_event = Event()
        self._label1_event = Event()
        self._event = Event()
        sleep(2)   

    def __get_prompt(self):   
        if self._label0_event.is_set():
            return 'Press \'q\' to extract a new features vector with label 0...'
        elif self._label1_event.is_set():
            return 'Press \'q\' to extract a new features vector with label 1...'
        else:
            return 'Press \'q\' to take a pick...'

    @property
    def label(self):
        if self._label0_event.is_set():
            return 0
        elif self._label1_event.is_set():
            return 1
        else:
            return None

    def __get_serial_port(self, baudrate, timeout):
        for port in serial.tools.list_ports.comports():
            try:
                return serial.Serial(port=str(port).split(' ')[0], baudrate=baudrate, timeout=timeout)
            except serial.serialutil.SerialException:
                continue
        raise serial.serialutil.SerialException()          

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
                    logging.info('\nBRIDGE CONNECTED\n')
                    self.websocket = websocket
                    while True:
                        weights = await receive_large_obj_over_ws(self.websocket)
                        logging.info(f"[Bridge]: --> received {len(weights)} bytes")
                        weights = pickle.loads(weights)
                        self.model.classifier.load_state_dict(weights, strict=True)
                        logging.info(f"[Bridge]: --> weights loading completed")
            except ConnectionRefusedError:
                await asyncio.sleep(3)

    async def send_features_vector(self, features_vector, label):
        await self.__check_connection()
        features_vector = features_vector.squeeze(0)
        features_vector = pickle.dumps(features_vector)
        await self.websocket.send((features_vector, label.to_bytes(1, 'little')))
        logging.info(f"[Bridge]: --> sent features vector to server")    

    def __correct_stdout(self):
        clear_screen()
        print(f'{self.__get_prompt()}', flush=True)    

    def take_picture(self):
            clear_screen()
            self._cam.open(self.__camera)
            ret, frame = self.__show_video()
            self._event.set()
            # self._cam.release()
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = transforms.functional.to_tensor(frame)
            img = img.unsqueeze(0)
            img = torch.nn.functional.interpolate(img, size=(224, 224))
            result = None
            
            with torch.no_grad():
                # import matplotlib.pyplot as plt
                # plt.imshow(img.squeeze(0).permute(1,2,0))
                # plt.show()
                
                if self.label == 0:
                    result = self.model.get_feature_vector(img)
                    self._loop.create_task(self.send_features_vector(result, 0))
                    clear_screen()
                    self._label0_event.clear()
                    self._event.clear()
                    return
                elif self.label == 1:
                    result = self.model.get_feature_vector(img)
                    self._loop.create_task(self.send_features_vector(result, 1))
                    clear_screen()
                    self._label1_event.clear()
                    self._event.clear()
                    return
                else:
                    predictions = self.model(img)
                    result = torch.argmax(predictions, 1).squeeze(0)
                    print(f"Label: {'CORRECT' if result.item() == 1 else 'INCORRECT'}")
                    self._event.clear()
                    return result.item()

    def __classification_loop(self):
        while True:
            result = self.take_picture()
            if result == 1:
                self.turn_on('correct')
            elif result == 0:
                self.turn_on('incorrect')

    def __show_video(self):
        while self._cam.isOpened():
            ret, frame = self._cam.read()
            if ret == True:
                cv2.imshow('Frame',frame)

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    # cv2.destroyAllWindows()
                    return ret, frame
            else:
                break

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
            #self.read()
            sleep(4)
            self.arduino.write(bytes(b'\xff'))
            self.arduino.write(bytes(b'\x01'))
            self.arduino.write(bytes(b'\xfe'))
            sleep(0.5)
            #self.read()
            sleep(0.5)
        if device == 'incorrect': 
            self.arduino.write(bytes(b'\xff'))
            self.arduino.write(bytes(b'\x02'))
            self.arduino.write(bytes(b'\x01'))
            self.arduino.write(bytes(b'\xfe'))
            sleep(0.5)
            #self.read()
            sleep(4)
            self.arduino.write(bytes(b'\xff'))
            self.arduino.write(bytes(b'\x02'))
            self.arduino.write(bytes(b'\xfe'))
            sleep(0.5)
            #self.read()
            sleep(0.5)

    #TODO remove read fuction (just for debugging)
    def read(self):
        data = self.arduino.readline().decode('ascii')
        print(data)

    def read_msg(self, msg):
        if msg[0] != b'\xff':
            return 0
        if msg[1] != b'\x03':
            return 0
        if msg[2] == b'\x01':
            return 1
        elif msg[2] == b'\x02':
            return 2

    def is_waiting(self):
        return True

    def loop(self):
        msg = []
        while True:
            if self.arduino.in_waiting > 0:
                while self._event.is_set():
                    continue                            # wait for current picture being processed
                recieved = self.arduino.read(1)
                if recieved == b'\xfe':
                    if len(msg) != 3:
                        msg = []
                    else:
                        response = self.read_msg(msg)
                        if response != 0 and not self._label0_event.is_set() and not self._label1_event.is_set():
                            if response == 1:
                                self._label1_event.set()
                            if response == 2:
                                self._label0_event.set()
                            self.__correct_stdout()
                        msg = []
                else:
                    msg.append(recieved)
    
    def __start(self):
        self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(self.receive_weights())
        self._loop.run_forever()

    def start(self):
        t1 = Thread(target=self.__start, name='bridge_websocket')
        t2 = Thread(target=self.__classification_loop, name='bridge_classification_loop')
        t1.start()
        t2.start()
        self.loop()
        # self.close()


if __name__ == '__main__':
    br = Bridge()
    br.start()
