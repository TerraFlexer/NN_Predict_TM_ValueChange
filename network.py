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

#variable for loading network or training new
testing = 0

final = []
test = []

#columns count in finals a.k. (amount of input) + (amount of output)
fcnt_inp = []

#colimns count in tests a.k. (amount of input) + (amount of output)
tcnt_inp = []

for fin in final_src:
	final.append(pd.read_csv(fin))
	fcnt_inp.append(len(final[-1].count()) - 5)
for tes in test_src:
	test.append(pd.read_csv(tes))
	tcnt_inp.append(len(test[-1].count()) - 5)


#creating the nn model
class Net(nn.Module):
	def __init__(self, inpdens, dens1, dens2):
		super(Net, self).__init__()
		self.fc1 = nn.Linear(inpdens, dens1)
		self.fc2 = nn.Linear(dens1, dens2)
		self.fc3 = nn.Linear(dens2, 1)
	def forward(self, x):
		x = self.fc1(x)
		x = nn.ReLU()(x)
		x = self.fc2(x)
		x = nn.ReLU()(x)
		x = self.fc3(x)
		return x


X = []
Y = []
tX = []
tY = []

#separating input and output train data and converting it to tensor
for fin in final:
	trainx = fin.drop("Value_Change", axis=1)
	trainx = trainx.drop("Player", axis = 1)
	trainx = trainx.drop("Squad", axis = 1)
	trainx = trainx.drop("Pos", axis = 1)
	trainx = trainx.drop("Cl_Squad", axis = 1)
	trainy = fin["Value_Change"]
	X.append(torch.Tensor(trainx.values))
	Y.append(torch.Tensor(trainy.values))

#separating input and output testing data and converting it to tensor
for tes in test:
	testx = tes.drop("Value_Change", axis=1)
	testx = testx.drop("Player", axis = 1)
	testx = testx.drop("Squad", axis = 1)
	testx = testx.drop("Pos", axis = 1)
	testx = testx.drop("Cl_Squad", axis = 1)
	testy = tes["Value_Change"]
	tX.append(torch.Tensor(testx.values))
	tY.append(torch.Tensor(testy.values))

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
	#function for training and testing
	def fit(model, X, Y, optimizer, llambda, batch_size=50, train=True):
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

	def test(model, X, Y, llambda, batch_size=30):
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


	#learning rate for networks
	learning_rate = 0.000025

	#creating models and optimizers for them
	models = []
	optimizers = []
	for i in range(3):
		models.append(Net(fcnt_inp[i], 200, 100))
		optimizers.append(torch.optim.Adam(models[i].parameters(), lr=learning_rate))  

	#creating arrays with dots for graph
	x = [[], [], []]
	y = [[], [], []]
	vy = [[], [], []]

	def train(epochs, model, X, Y, gx, gy, gvy, tX, tY, optimizer):
		for epoch in range(epochs):
			L = fit(model, X, Y, optimizer, 0.001)
			vL = test(model, tX, tY, 0.001)
			#print(f'epoch: {epoch:5d} loss: {L:.4f}' )
			if ((epoch % 10) == 0):
				print(f'epoch: {epoch:5d} loss: {L:.4f}, validation_loss: {vL:.4f}')
			gx.append(epoch)
			gy.append(L)
			gvy.append(vL)

	for i in range(3):
		train(500, models[i], X[i], Y[i], x[i], y[i], vy[i], tX[i], tY[i], optimizers[i])
		plt.plot(x[i], y[i], 'g-', x[i], vy[i], 'r-')
		plt.xlabel(r'$epoch$')
		plt.ylabel(r'$loss$')
		plt.title(r'$loss$')
		plt.show()