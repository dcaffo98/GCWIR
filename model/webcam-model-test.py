import cv2
import torch
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.pyplot as plt

if __name__ == '__main__':
    import os, sys
    sys.path.append(os.getcwd())

from torchvision import transforms
from model.masked_face_vgg import MaskedFaceVgg
from server.fake_bridge import FakeBridge
from server.srv import Server
from client.client import Client

client = Client()
server = Server()
bridge = FakeBridge()
import asyncio 

# check camera number
CAMERA = 1

vgg = MaskedFaceVgg()
cam = cv2.VideoCapture(CAMERA)

async def foo():
    while True:
        go = input('Press enter to take a pick...')
        cam.open(CAMERA)
        ret, frame = cam.read()
        cam.release()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # cv2.imwrite('pic.jpg', frame)
        t = transforms.functional.to_tensor(frame)
        t = t.unsqueeze(0)
        t = torch.nn.functional.interpolate(t, size=(224, 224))

        # TODO: fix torch.no_grad() causing "RuntimeError: element 0 of tensors does not require grad and does not have a grad_fn"
        # with torch.no_grad():
        # plt.imshow(t.squeeze(0).permute(1,2,0))
        # plt.show()
        predictions = vgg(t)     
        features_vector = vgg.get_feature_vector(t)
        result = torch.argmax(predictions, 1).squeeze(0)
        features_vector = features_vector.requires_grad_()
        await bridge.send_features_vector(features_vector, result.item())
        print(f"Label: {'CORRECT' if result.item() == 1 else 'INCORRECT'}")
        await asyncio.sleep(30)


asyncio.get_event_loop().run_until_complete(asyncio.gather(*server.start()))
asyncio.get_event_loop().run_until_complete(asyncio.gather(client.request_samples(), bridge.receive_weights(), foo()))
asyncio.get_event_loop().run_forever()
