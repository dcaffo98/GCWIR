import serial
from time import sleep

class Bridge():
    def __init__(self):
        self.arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.5)
        sleep(2)

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


if __name__ == '__main__':
    br=Bridge()
    br.loop()
    br.close()

#x = vgg.getfeaturevector()