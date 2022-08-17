import torch
import numpy as np
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import pandas as pd
import matplotlib.pyplot as plt
import env


final_src = env.final_csv
testing = 1
learning_rate = 0.0025

final = pd.read_csv(final_src)

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


model = Net(150, 100, 100)

#separating input and output data
trainx = final.drop("Value_Change", axis=1)
trainy = final["Value_Change"]

#converting data to the torch tensor
X = torch.Tensor(trainx.values)
Y = torch.Tensor(trainy.values)

if (testing):
	model.load_state_dict(torch.load(env.nn_state_dict))
	model.eval()
	for i in range(250, 500):
		print(model(X[i]), " ", Y[i])
else:
	optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)   
	loss = nn.MSELoss()

	#function for training and testing
	def fit(model, X, Y, optimizer, batch_size=40, train=True):
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

	#creating arrays with dots for graph
	x = []
	y = []

	epochs = 6000
	coeff = 10
	for epoch in range(epochs):
		L = fit(model, X, Y, optimizer)
		if (epoch % 1500 == 0 and epoch != 0):
			learning_rate /= coeff
			optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
			coeff /= 2
		#print(f'epoch: {epoch:5d} loss: {L:.4f}' )
		if ((epoch % 10) == 0):
			print(f'epoch: {epoch:5d} loss: {L:.4f}' )
		x.append(epoch)
		y.append(L)

	#saving model_state_dict
	torch.save(model.state_dict(), env.nn_state_dict)

	#creating graph
	plt.plot(x, y)
	plt.xlabel(r'$epoch$')
	plt.ylabel(r'$loss$')
	plt.title(r'$loss$')
	plt.show()