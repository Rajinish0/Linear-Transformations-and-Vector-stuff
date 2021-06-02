import numpy as np
from scipy import special
from sklearn.datasets import load_iris,load_digits,load_breast_cancer
import matplotlib.pyplot as plt

class Layer():
	def __init__(self,inNodes, outNodes,activation='linear'):
		self.inNodes = inNodes
		self.outNodes = outNodes		
		self.activation = activation
		self.weights,self.bias = self.GetWeights()	
		self.activationF = self.GetActivationF()

	def GetWeights(self):
		weights = np.random.randn(self.outNodes,self.inNodes)*.01
		bias = np.random.randn(self.outNodes,1)*.01
		return (weights,bias)

	def __repr__(self):
		return f'Weights : ({self.inNodes},{self.outNodes})\nBias : ({self.outNodes})\nActivation : {self.activation}'

	def GetActivationF(self):
		if self.activation == 'linear':
			return (lambda x : x)

		elif self.activation == 'relu':
			return lambda x : np.maximum(0,x)

		elif self.activation == 'sigmoid':
			return lambda x: special.expit(x)

		elif self.activation == 'tanh':
			return lambda x: np.tanh(x)

		elif self.activation == 'softmax':
			def f(x):
				t = np.exp(x)
				div = np.sum(t, axis=0, keepdims=True)
				r = t/div
				r[(r == np.inf) | (r==-np.inf)] = 0
				return r

			return f

		else:
			raise Exception(f'{self.activation} is invalid')

	def GetActivationDerivative(self):
		if self.activation == 'linear':
			return (lambda x : 1)(self.a)

		elif self.activation == 'relu':
			return (lambda x : np.where(x<0,0,1))(self.a)

		elif self.activation == 'sigmoid':
			return (self.a*(1-self.a))
		elif self.activation == 'tanh':
			return (1-(self.a*self.a))

		else:
			raise Exception(f'{self.activation} is invalid')		

	def __call__(self,X):
		self.prev_a = X.copy()
		self.z = (self.weights@X + self.bias)
		self.a = self.activationF(self.z)
		return self.a

	def Update(self,alpha):
		self.weights = self.weights - alpha*self.dW
		self.bias = self.bias - alpha*self.db


class Model():
	def __init__(self,layers=[]):
		self.layers = layers

	def addLayer(self,layer):
		self.layers.append(layer)

	def __call__(self,X):
		return self.predict(X)

	def predict(self,X):
		out = X
		for layer in self.layers:
			out = layer(out)
		return out

	def __repr__(self):
		for i,each in enumerate(self.layers):
			print('-'*50)
			print('Layer ' + str(i))
			print(each)
		return ''

	def backward(self,y):
		for i, each in reversed(list(enumerate(self.layers))):

			if i != len(self.layers)-1:
				each.dA = self.layers[i+1].weights.T@self.layers[i+1].dZ
				each.dZ = each.dA*each.GetActivationDerivative()
			else:
				each.dZ = each.a - y
			each.dW = each.dZ@each.prev_a.T
			each.db = np.sum(each.dZ,axis=1,keepdims=True)
		return self


	def train(self,X,y,Metric,alpha=.01,epochs=10):
		for _ in range(epochs):
			pred = self.predict(X)
			print(f'EPOCH : {_+1} Accuracy : {Metric(pred,y)}',end='\r')
			self.backward(y)
			[each.Update(alpha) for each in self.layers]


def BinaryAccuracy(pred,y):
	pred[pred>=.5]=1
	pred[pred <=.5]=0
	return (pred == y).mean()

def MLabelAccuracy(pred,y):
	return (np.argmax(pred,axis=0)==np.argmax(y,axis=0)).mean()




d = load_digits() 

X,y = d['data'], d['target']
inds = np.random.permutation(len(X))
cutOff = round(.8*len(X))

ny = np.zeros((len(X),10))
ny[np.arange(len(X)), y] = 1
X= X.T
ny = ny.T


l1 = Layer(64,64,activation='sigmoid')
l2 = Layer(64,10,activation='softmax')
m = Model([l1,l2])
# m.addLayer(l2)
# m.addLayer(l3)

m.train(X,ny,Metric= MLabelAccuracy,alpha=1e-5,epochs=500)

# labels = m(X).argmax(axis=0)
# for i in range(10):
# 	plt.subplots()
# 	plt.imshow(X.T[i].reshape(8,8))
# 	print(labels[i])
# 	plt.show()
