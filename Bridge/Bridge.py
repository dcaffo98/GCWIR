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
            self.arduino.write(bytes(b'1'))
            sleep(0.5)
            self.read()
            sleep(4)
            self.arduino.write(bytes(b'2'))
            sleep(0.5)
            self.read()
            sleep(0.5)
        if device == 'incorrect': 
            self.arduino.write(bytes(b'3'))
            sleep(0.5)
            self.read()
            sleep(4)
            self.arduino.write(bytes(b'4'))
            sleep(0.5)
            self.read()
            sleep(0.5)


    def read(self):
        data = self.arduino.readline().decode('ascii')
        print(data)

    def is_waiting(self):
        return True

    def loop(self):
        while True:
            if self.is_waiting():
                self.turn_on('correct')
            else:
                print(self.arduino.in_waiting)
                if self.arduino.in_waiting>0:
                    self.read()
            self.read()

if __name__ == '__main__':
    br=Bridge()
    br.loop()
    br.close()

