## USING PROJECTIONS FROM LINEAR ALGEBRA TO GET APPROXIMATIONS OF ARBITRARY FUNCTIONS.
## The error b/w approx - actual is minimal when approx is the projection of the function onto the range of the polynomial or any other function we're using to approximate that function.


from functools import reduce
import math, copy
from math import sin,cos,pi
import numpy as np
import matplotlib.pyplot as plt
def dot(funcs,upperBound,lowerBound,dx=.01):

	assert type(funcs) == list

	x = lowerBound
	tSum = 0
	sign = 1 if upperBound > lowerBound else -1

	check = lambda x : x < upperBound if sign == 1 else x > upperBound

	## <f,g> = integral from lowerBound to upper bound of (f*g)
	while check(x):
		tSum += reduce(lambda x,y :x*y, [f(x) for f in funcs])*dx
		x += dx*sign
	return sign*tSum

def GetPolynomials(degree=5):
	poly= []
	for i in range(degree+1):
		def f(x,i=i):
			return x**i

		poly.append(f)
	return poly


## TO GET ORTHONORMAL BASES FOR THE POLYNOMIAL
def GramSchmidt(polys):
	global upperBound, lowerBound
	orthoGonalPoly = []
	for i, each in enumerate(polys):
		projs = []

		# SO since each basis in orthogonalPoly is normalized, i can just dot this basis with previous ones to get the projections onto them
		# <each,ej> for 0<=j<i
		for f in orthoGonalPoly:
			projs.append(dot([each,f],upperBound,lowerBound))


		## now just subtracting those projections to make it orthogonal to those bases.
		## so each - <each,ej>*ej
		def orthogonalFunc(x,projs=copy.deepcopy(projs), curFunc = copy.copy(each),orthoGonalFuncs=copy.deepcopy(orthoGonalPoly)):
			s = curFunc(x)
			for ind,func in enumerate(orthoGonalFuncs):
				s -= func(x)*projs[ind]
			return s

		## Normalizing each bases to make them orthonormal
		d = math.sqrt(dot([orthogonalFunc,orthogonalFunc],upperBound,lowerBound))
		def orthonormalFunc(x, orthogonalFunc=copy.deepcopy(orthogonalFunc),d=d):
			s = orthogonalFunc(x)			
			return s/d

		orthoGonalPoly.append(orthonormalFunc)

	return orthoGonalPoly


def GetApprox(f,orthoGonalPoly):
	approxPoly = []

	## so the best approx is the projection of the function onto the range of the polynomial
	## which is just <f,ej>*ej, bcz each ej is normalized.
	for i,each in enumerate(orthoGonalPoly):
		def func(x,curFunc=copy.copy(each)):
			return dot([f,curFunc],upperBound,lowerBound)*curFunc(x)
		approxPoly.append(func)
	return approxPoly



upperBound, lowerBound = pi,-pi
degree = 5
funcToApproximate = sin

polys = GetPolynomials(degree)
orthoGonalPoly =  GramSchmidt(polys)
approxPoly = GetApprox(funcToApproximate,orthoGonalPoly)
## UH [f(1) for f in approxPoly] does not give the coefficients on each of the basis vectors 1,..xn.
## bcz for example since the second basis vector = normalized(v2 - projontov1 of v2), f(1) on this basis vector doesn't necessarily give
## x's coefficient.


polynomial = lambda x: sum([f(x) for f in approxPoly])

def fact(n):
	if n <= 1:
		return 1
	return n*fact(n-1)

def GetTaylor():
	global degree
	taylor = []
	pos = 1
	for i in range(degree+1):	
		def func(x,i=i,pos=copy.copy(pos)):
			return (x**i)/fact(i)*(-1)**(pos+1)		

		if i % 2 == 1:
			taylor.append(func)
			pos = not pos
	return taylor
taylor = GetTaylor()
tF = lambda x: sum([f(x) for f in taylor])




ar = np.arange(lowerBound,upperBound,.1)

plt.plot(ar,np.sin(ar), c='r',label='sin')
plt.plot(ar,polynomial(ar),c='b', label=f'poly deg: {degree}')
plt.plot(ar,tF(ar),c='g', label='taylor')
plt.legend()
plt.show()

