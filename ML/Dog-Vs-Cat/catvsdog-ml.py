import torch
import torchvision
from torchvision import transforms
from PIL import Image
from os import listdir
import random
import torch.optim as optim
from torch.autograd import Variable
import torch.nn.functional as F
import torch.nn as nn

normalize = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(256),
    transforms.ToTensor(),
    normalize])

# TARGET: [isCat, isDog]
train_data_list = []
target_list = []
train_data = []
waited = False
files = listdir(r"C:\Users\yasin\Desktop\PyCharm\catdog")
for i in range(len(listdir(r"C:\Users\yasin\Desktop\PyCharm\catdog"))):
    if len(train_data) == 58 and not waited:
        waited = True
        continue
    f = random.choice(files)
    files.remove(f)
    img = Image.open(r"C:\Users\yasin\Desktop\PyCharm\catdog\\" + f)
    img_tensor = transform(img)  # (3, 256, 256)
    train_data_list.append(img_tensor)
    isCat = 1 if 'cat' in f else 0
    isDog = 1 if 'dog' in f else 0
    target = [isCat, isDog]
    target_list.append(target)
    if len(train_data_list) >= 64:
        train_data.append((torch.stack(train_data_list), target_list))
        train_data_list = []
        target_list = []
        print('Loaded batch', len(train_data), 'of', int(len(listdir(r"C:\Users\yasin\Desktop\PyCharm\catdog")) / 64))
        print('Percentage Done: ', 100 * len(train_data) / int(len(listdir(r"C:\Users\yasin\Desktop\PyCharm\catdog")) / 64), '%')
        if len(train_data) > 1:  # Batch
            break


class Netz(nn.Module):
    def __init__(self):
        super(Netz, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)
        self.conv2 = nn.Conv2d(6, 12, kernel_size=5)
        self.conv3 = nn.Conv2d(12, 18, kernel_size=5)
        self.conv4 = nn.Conv2d(18, 24, kernel_size=5)
        self.fc1 = nn.Linear(3456, 1000)
        self.fc2 = nn.Linear(1000, 2)

    def forward(self, x):
        x = self.conv1(x)
        x = F.max_pool2d(x, 2)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.max_pool2d(x, 2)
        x = F.relu(x)
        x = self.conv3(x)
        x = F.max_pool2d(x, 2)
        x = F.relu(x)
        x = self.conv4(x)
        x = F.max_pool2d(x, 2)
        x = F.relu(x)
        x = x.view(-1, 3456)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.sigmoid(x)


model = Netz()
model.cpu()

optimizer = optim.Adam(model.parameters(), lr=0.05)


def train(epoch):
    model.train()
    batch_id = 0
    for data, target in train_data:
        data = data.cpu()
        target = torch.Tensor(target).cpu()
        data = Variable(data)
        target = Variable(target)
        optimizer.zero_grad()
        out = model(data)
        criterion = F.binary_cross_entropy
        loss = criterion(out, target)
        loss.backward()
        optimizer.step()
        print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
            epoch, batch_id * len(data), len(train_data),
            100. * batch_id / len(train_data), loss.item()))
        batch_id = batch_id + 1


def test():
    model.eval()
    files = listdir(r"C:\Users\yasin\Desktop\PyCharm\test")
    f = random.choice(files)
    img = Image.open(r"C:\Users\yasin\Desktop\PyCharm\test\\" + f)
    img_eval_tensor = transform(img)
    img_eval_tensor.unsqueeze_(0)
    data = Variable(img_eval_tensor.cpu())
    out = model(data)
    print(out.data.max(1, keepdim=True)[1])
    img.show()
    x = input('Press enter: ')


for epoch in range(1, 30):
    train(epoch)
    test()
