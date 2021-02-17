import cv2
import torch
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms
import os, sys

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from model.masked_face_vgg import MaskedFaceVgg


# check camera number
CAMERA = 1

vgg = MaskedFaceVgg()
cam = cv2.VideoCapture(CAMERA)

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

    with torch.no_grad():
        plt.imshow(t.squeeze(0).permute(1,2,0))
        plt.show()
        predictions = vgg(t)            
        results = torch.argmax(predictions, 1)
        for res in results:
            print(f"Label: {'CORRECT' if res == 1 else 'INCORRECT'}")