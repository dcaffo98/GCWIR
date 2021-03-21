import asyncio
import os, sys
from time import sleep

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from server.srv import Server
from client.client import Client
from bridge.bridge import Bridge
from utils.configurator import Configurator

configurator = Configurator()

server = Server(address=configurator.get('Server', 'address'), model_port=configurator.get('Server', 'model_port'), bridge_port=configurator.get('Server', 'bridge_port'))
client = Client(server_uri=configurator.get('Client', 'server_uri'))
bridge = Bridge(server_uri=configurator.get('Bridge', 'server_uri'))

server.start()
client.start()
bridge.start()
