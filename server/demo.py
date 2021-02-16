import asyncio
from server import Server
from client.client import Client
from fake_bridge import FakeBridge
from utils.configurator import Configurator

configurator = Configurator()

server = Server(address=configurator.get('Server', 'address'), model_port=configurator.get('Server', 'model_port'), bridge_port=configurator.get('Server', 'bridge_port'))
client = Client(server_uri=configurator.get('Client', 'server_uri'))
bridge = FakeBridge(server_uri=configurator.get('Bridge', 'server_uri'))

asyncio.get_event_loop().run_until_complete(asyncio.gather(*server.start()))
asyncio.get_event_loop().run_until_complete(asyncio.gather(client.request_samples(), bridge.foo()))
asyncio.get_event_loop().run_forever()
