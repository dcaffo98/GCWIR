import torch 
import torch.nn as nn
import torchvision.models as models
import torchvision
import matplotlib.pyplot as plt
import os, sys

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from dataset.dataset import LazyDataset
from model.masked_face_vgg import MaskedFaceVgg


vgg = MaskedFaceVgg()


trainset = LazyDataset(mode='train')
trainloader = torch.utils.data.DataLoader(trainset, batch_size=32, shuffle=True, num_workers=6)

testset = LazyDataset(mode='test')
testloader = torch.utils.data.DataLoader(testset, batch_size=32, shuffle=True, num_workers=6)


assert torch.cuda.is_available(), "Notebook is not configured properly!"
device = 'cuda:0'

cross_entropy = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(vgg.parameters(), lr=0.001, momentum=0.9)
epochs = 10

vgg = vgg.to(device)
torch.save(vgg.state_dict(), 'x.pth')

for epoch in range(epochs):
    for samples, labels in trainloader:
        samples, labels = samples.to(device), labels.to(device)
        # plt.title(f"{'CORRECT' if labels[9].item() == 1 else 'INCORRECT'}")
        # img = samples[9, ...].permute(1, 2, 0).to('cpu')
        # plt.imshow(img)
        # plt.show()
        predictions = vgg(samples)
        correct = 0
        correct += (torch.max(predictions, 1)[1] == labels).sum()
        print(f"Accuracy for epoch {epoch}:\t{correct / len(samples)}")
        loss = cross_entropy(predictions, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    correct = 0

    for samples, labels in testloader:
        samples, labels = samples.to(device), labels.to(device)
        predictions = vgg(samples)
        correct += (torch.max(predictions, 1)[1] == labels).sum()
    
    print(f"Accuracy for epoch {epoch}:\t{correct / len(testset)}")


# save weights
torch.save(vgg.state_dict(), 'x.pth')