import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import pandas as pd
import matplotlib.pyplot as plt
import env

final_src = env.final_csv

final = pd.read_csv(final_src)

cnt_inp = len(final.count())

class Net(nn.Module):
	def __init__(self):
		super(Net, self).__init__()
		self.fc1 = nn.Linear(cnt_inp - 1, 200)
		self.fc2 = nn.Linear(200, 50)
		self.fc3 = nn.Linear(50, 1)
	def forward(self, x):
		x = self.fc1(x)
		x = nn.ReLU()(x)
		x = self.fc2(x)
		x = nn.ReLU()(x)
		x = self.fc3(x)
		return x

model = Net()

optimizer = torch.optim.Adam(model.parameters(), lr=0.0005)   
loss = nn.MSELoss()

testx = final.drop("Value_Change", axis=1)
testy = final["Value_Change"]

X = torch.Tensor(testx.values)
X = nn.Sigmoid()(X)
Y = torch.Tensor(testy.values)
Y = nn.Sigmoid()(Y)


def fit(model, X, Y, batch_size=50, train=True):
	model.train(train)
	sumL, sumA, numB = 0, 0, int(len(X) / batch_size)
       
	for i in range(0, numB * batch_size, batch_size):          
		idx = torch.randint(high = len(X), size = (batch_size,) )
		xb = X[idx]                               
		yb = Y[idx]

		y = model(xb)
		L = loss(torch.reshape(y, (batch_size,)), yb)

		if train:
			optimizer.zero_grad()
			L.backward()
			optimizer.step()

		sumL += L.item()

	return sumL / numB

print( "before:      loss: %.4f" % fit(model, X,Y, train=False) )

x = []
y = []

epochs = 3500                                        # число эпох
for epoch in range(epochs):                              # эпоха - проход по всем примерам
	L = fit(model, X, Y)                               # одна эпоха                 
	print(f'epoch: {epoch:5d} loss: {L:.4f}' )
	if ((epoch % 10) == 0):
		x.append(epoch)
		y.append(L)

plt.plot(x, y)
plt.xlabel(r'$epoch$')
plt.ylabel(r'$loss$')
plt.title(r'$loss$')
plt.show()