import torch
import numpy as np
from torch.autograd import Variable
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import matplotlib.pyplot as plt
import env


final_src = env.final_csv
test_src = env.test_csv
testing = 0
learning_rate = 0.0025

final = pd.read_csv(final_src)
test = pd.read_csv(test_src)

#columns count a.k. (amount of input) + (amount of output)
cnt_inp = len(final.count())

#creating the nn model
class Net(nn.Module):
	def __init__(self, dens1, dens2, dens3):
		super(Net, self).__init__()
		self.fc1 = nn.Linear(cnt_inp - 1, dens1)
		self.fc2 = nn.Linear(dens1, dens2)
		self.fc3 = nn.Linear(dens2, dens3)
		self.fc4 = nn.Linear(dens3, 1)
	def forward(self, x):
		x = self.fc1(x)
		x = nn.ReLU()(x)
		x = self.fc2(x)
		x = nn.ReLU()(x)
		x = self.fc3(x)
		x = nn.ReLU()(x)
		x = self.fc4(x)
		return x


model = Net(200, 200, 150)
model1 = Net(300, 200, 150)

#separating input and output train data
trainx = final.drop("Value_Change", axis=1)
trainy = final["Value_Change"]

#converting train data to the torch tensor
X = torch.Tensor(trainx.values)
Y = torch.Tensor(trainy.values)

#separating testing input and output data
testx = test.drop("Value_Change", axis=1)
testy = test["Value_Change"]

#converting testing data to the torch tensor
tX = torch.Tensor(testx.values)
tY = torch.Tensor(testy.values)

loss = nn.MSELoss()


if (testing):
	model.load_state_dict(torch.load(env.nn_state_dict))
	model.eval()
	y = model(tX)
	print(y.size()[0])
	for i in range(y.size()[0]):
		print(i, " ", y[i][0], " ", tY[i])

	L = loss(y, tY)
	print(L / len(tY))
else:
	optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)   
	optimizer1 = torch.optim.Adam(model1.parameters(), lr=learning_rate)
	loss = nn.MSELoss()

	#function for training and testing
	def fit(model, X, Y, optimizer, llambda, batch_size=70, train=True):
		model.train(train)
		sumL, sumA, numB = 0, 0, int(len(X) / batch_size)
       
		for i in range(0, numB * batch_size, batch_size):
			idx = torch.randint(high = len(X), size = (batch_size,) )
			xb = X[idx]                               
			yb = Y[idx]

			y = model(xb)
			L = loss(torch.reshape(y, (batch_size,)), yb)

			l2_lambda = llambda
			l2_norm = sum(p.pow(2.0).sum() for p in model.parameters())

			L += l2_lambda * l2_norm

			if train:
				optimizer.zero_grad()
				L.backward()
				optimizer.step()

			sumL += L.item()

		return sumL / numB

	def test(model, X, Y, llambda, batch_size=70):
		model.eval()
		sumL, sumA, numB = 0, 0, int(len(X) / batch_size)
		for i in range(0, numB * batch_size, batch_size):
			idx = torch.randint(high = len(X), size = (batch_size,) )
			xb = X[idx]                               
			yb = Y[idx]

			y = model(xb)
			L = loss(torch.reshape(y, (batch_size,)), yb)

			l2_lambda = llambda
			l2_norm = sum(p.pow(2.0).sum() for p in model.parameters())

			L += l2_lambda * l2_norm

			sumL += L.item()

		return sumL / numB

	#creating arrays with dots for graph
	x = []
	y = []
	vy = []
	y1 = []
	vy1 = []

	epochs = 400
	coeff = 10
	for epoch in range(epochs):
		L = fit(model, X, Y, optimizer, 0.001)
		vL = test(model, tX, tY, 0.001)
		if (epoch % 200 == 0 and epoch != 0):
			learning_rate /= coeff
			optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
			coeff /= 2
		#print(f'epoch: {epoch:5d} loss: {L:.4f}' )
		if ((epoch % 10) == 0):
			print(f'epoch: {epoch:5d} loss: {L:.4f}, validation_loss: {vL:.4f}')
		x.append(epoch)
		y.append(L)
		vy.append(vL)

	learning_rate = 0.0025
	coeff = 10
	for epoch in range(epochs):
		L = fit(model1, X, Y, optimizer1, 0.001)
		vL = test(model1, tX, tY, 0.001)
		if (epoch % 200 == 0 and epoch != 0):
			learning_rate /= coeff
			optimizer1 = torch.optim.Adam(model1.parameters(), lr=learning_rate)
			coeff /= 2
		#print(f'epoch: {epoch:5d} loss: {L:.4f}' )
		if ((epoch % 10) == 0):
			print(f'epoch: {epoch:5d} loss: {L:.4f}, validation_loss: {vL:.4f}')
		y1.append(L)
		vy1.append(vL)

	#saving model_state_dict
	torch.save(model.state_dict(), env.nn_state_dict)

	#creating graph
	plt.plot(x, y, 'g-', x, vy, 'r-', x, y1, 'b-', x, vy1, 'y-')
	plt.xlabel(r'$epoch$')
	plt.ylabel(r'$loss$')
	plt.title(r'$loss$')
	plt.show()