import pygame,random,math,time,copy,sys,threading, numpy as np
from seein import Vector, Matrix
from vf import DiffRootVector
run = True
w,h = 1200,600
alteredW = 1500
alteredH = 1500
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
scale = 50
depth = 150 ## Z depth for three d plane

def CheckEvent():
	global run, ang, mouseIsDown, origXPos, origYPos,disT
	gotOrigPos = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN:

			if event.button == 4:
				disT -= (6)

			elif event.button == 5:
				disT += (6)

			elif not gotOrigPos:
				origXPos, origYPos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
				gotOrigPos = True
				mouseIsDown= True


		if event.type == pygame.MOUSEBUTTONUP:
			gotOrigPos = False
			mouseIsDown = False

		if mouseIsDown:
			SetAngle()

	keys = pygame.key.get_pressed()
	return (keys,run)

def GetBasisVectors():
	global endPoints
	v1 = endPoints[0][0]
	v2 = endPoints[1][0]

	v3 = endPoints[-2][0]
	v4 = endPoints[-1][0]
	threshold = Vector(w//2,h//2)

	x1 = v2-v1
	x2 = v4-v3


	ihat = DiffRootVector(threshold,*(x1),clampMagnitude=False)
	jhat = DiffRootVector(threshold,*(x2),clampMagnitude=False)
	return (ihat,jhat)
	

def drawBasisVectors():
	global ProjectIn3d,testVectors
	if not ProjectIn3d:
		i,j = GetBasisVectors()
		for bVectors in (i,j):
			bVectors.b, bVectors.r,bVectors.g = (255,255,255)
			bVectors.draw(screen)
		if testVectors is not None:
			vToTests = [DiffRootVector(Vector(w//2,h//2),*testVector,clampMagnitude=False) for testVector in testVectors] 
			for vToTest in vToTests:
				vToTest.b,vToTest.r,vToTest.g = (0,255,0)
				vToTest.draw(screen)


def EndPoints():
	global threeDoctant
	endPoints = GetEndPoints2d() if not threeDoctant else GetEndPoints3d()
	return endPoints		


def GetEndPoints2d():
	global scale,depth, threeDoctant
	endPoints = []
	for x in range(0,alteredW,scale):
		endPoints.append([Vector(x-alteredW//2,(alteredH//2)),Vector(x-alteredW//2,-(alteredH-alteredH//2))])
		func([DrawLines],Args=[
							  [endPoints,(51,81,121)]
							  ])
	for y in range(0,alteredH,scale):
		endPoints.append([Vector(0-(alteredW//2),-(y-alteredH//2)),Vector(alteredW-(alteredW//2),-(y-alteredH//2))])
		func([DrawLines],Args=[
							  [endPoints,(51,81,121)]
							  ])
	return endPoints


def GetEndPoints3d():
	global scale,depth, threeDoctant
	endPoints = []
	for z in range(0,depth,scale):
		for x in range(0,alteredW,scale):
			endPoints.append([Vector(x-alteredW//2,(alteredH//2),z),Vector(x-alteredW//2,-(alteredH-alteredH//2),z)])
			func([DrawLines],Args=[
								  [endPoints,(51,81,121)]
								  ])
		for y in range(0,alteredH,scale):
			endPoints.append([Vector(0-(alteredW//2),-(y-alteredH//2),z),Vector(alteredW-(alteredW//2),-(y-alteredH//2),z)])
			func([DrawLines],Args=[
								  [endPoints,(51,81,121)]
								  ])
	return endPoints


def constrain(cur,total,maximum):
    return ((cur*abs(maximum)*2)/total)-maximum

disT = 5
def projg(vert):
	global disT
	vert.x *= (1-(disT-vert.z/25)/100)
	vert.y *= (1-(disT-vert.z/25)/100)


ang = 0
angX = 0
def Get3dProjected(v):
	global ang,depth
	try:

		z = constrain(v.z,depth,25)
	except:
		z = constrain(v.y,alteredH,25)

	rotatedV = Vector(*v.elems[:2],z).RotationX(angX,Vector(0,0,0))
	rotatedV = rotatedV.RotationY(ang,Vector(0,0,0))
	ang += 0.001
	projg(rotatedV)
	return rotatedV

def DrawLines(l,c):
	global ProjectIn3d
	for i,(v1,v2) in enumerate(l):
		x1,y1,x2,y2 = v1.elems[:2]+v2.elems[:2]
		## 3D projected Rotation of the 2d plance
		if ProjectIn3d:
			nV1 = Get3dProjected(v1)
			nV2 = Get3dProjected(v2)
			pygame.draw.line(screen,c,(nV1.x+w//2,nV1.y+h//2),(nV2.x+w//2,nV2.y+h//2),2)
		else:
			pygame.draw.line(screen,c,(x1+w//2,y1+h//2),(x2+w//2,y2+h//2),2)


def func(funcsToCall=[], Args=None):
	global origEnds,origTestVectors
	screen.fill((0,0,0))

	try:
		DrawLines(origEnds,(21,21,51))
		if not ProjectIn3d:
			vToTests = [DiffRootVector(Vector(w//2,h//2),*origTestVector,clampMagnitude=False) for origTestVector in origTestVectors]
			for vToTest in vToTests:
				vToTest.b,vToTest.r = (51,51)
				vToTest.draw(screen)
	except:
		pass

	for i,func in enumerate(funcsToCall):
		func(*Args[i])

	pygame.display.update()
	CheckEvent()



def Lerp(a,b,percent):
	return (a+(b-a)*percent)

def adjustTransformation(T):
	origTrans = copy.deepcopy(T.mat)
	origTrans[1].x *= -1
	origTrans[0].y *= -1
	return Matrix(origTrans)

def SetAngle():
	global ang, angX
	ang = -1*(pygame.mouse.get_pos()[0] - origXPos)/5
	angX = -1*(pygame.mouse.get_pos()[1] - origYPos)/5


def applyTrans():
	global endPoints, T,testVectors, threeDoctant, ProjectIn3d
	percent = 0
	percentInc = .01 if not threeDoctant else .1
	IdentityMatrix = Matrix([[1,0],
							[0,1]])
	if threeDoctant:
		IdentityMatrix = Matrix([[1,0,0],
								[0,1,0],
								[0,0,1]])
	IM = {(2,2):Matrix([[1,0],
						[0,1]]),
	      (3,3):Matrix([[1,0,0],
	      				[0,1,0],
	      				[0,0,1]]),
	      (3,2):Matrix([[1,0],
	      				[0,1],
	      				[0,0]]),
	      (2,3):Matrix([[1,0,0],
	      				[0,1,0]])}
	
	origVs = copy.deepcopy(endPoints)
	origTests = copy.deepcopy(testVectors)
	Transformation = adjustTransformation(T) if Vector(2,2) == T.shape else T

	try:
		IdentityMatrix = IM[tuple(T.shape.elems)]
	except:
		pass

	while percent<=1:
		curTransformation = Lerp(IdentityMatrix,Transformation,percent)
		if curTransformation.shape[0] == 3:
				ProjectIn3d = True

		for i,(v1,v2) in enumerate(endPoints):
			endPoints[i] = (v1.applyTransformation(curTransformation),v2.applyTransformation(curTransformation))


		if testVectors != None and not ProjectIn3d:
			testVectors = [testVector.applyTransformation(curTransformation) for testVector in testVectors]

		func([DrawLines,clock.tick,drawBasisVectors],Args=[
							[endPoints,(51,81,121)],
								[20],
								[]
								 ])
		percent += percentInc
		percent = round(percent,2)
		endPoints = copy.deepcopy(origVs) if not percent>1 else endPoints
		testVectors = copy.deepcopy(origTests) if not percent>1 else testVectors


## SO YOU CAN PROJECT A 2d plane in 3d
ProjectIn3d = True

## OR YOU CAN HAVE A 3D PLANE
threeDoctant = False
if threeDoctant:
	ProjectIn3d = 1;

if ProjectIn3d:
	alteredW,alteredH = 500,500



mouseIsDown= False
origXPos = None
origYPos = None

endPoints = EndPoints()
origEnds = copy.deepcopy(endPoints)
eigs = list(np.linalg.eig(np.array([[1,1],
				[1,1]]))[1])
#eigs[0][1] *= -1
testVectors = [Vector(*eig)*scale*i for eig in eigs for i in range(-5,5)] ##y coord flipped
#testVectors = []
origTestVectors = [copy.copy(each) for each in testVectors]
Ts = {0:Matrix([[1,1,], 
			[-1,-1],
			[1,1]]),1:Matrix([[1,-1,1],
					[1,-1,1]])}
Ts = {0:Matrix([[1,1],
				[1,1]]),1:Matrix([[1,0],
								[0,1]])}
# Ts = {0:Vector(0,0,0).RotationOnX(90), 1:Matrix([[1,-1,0],
				# [1,2,0],
				# [1,2,3]])}

## VISUALIZING PSEUDO INVERSE OF THIS MATRIX
U,sigma,V = np.linalg.svd(np.array([[-1,1],
							[-1,1],
							[-1,2]]))

reverseSigma = np.diag(1/sigma)
sigma=np.diag(sigma)
U= U[:,1:]
Ts = [Matrix(V),Matrix(sigma),Matrix(U), Matrix(U.T),Matrix(reverseSigma), Matrix(V.T)]
curT = 0
T= Ts[curT]

if threeDoctant:
	assert (len(T.mat) == 3)

while run:
	func([DrawLines,drawBasisVectors],Args=[
						  [endPoints,(51,81,121)],
						  []
						  ])
	keys = pygame.key.get_pressed()
	if keys[pygame.K_a]:
			applyTrans()
			time.sleep(.1)

	if keys[pygame.K_r]:
		endPoints = EndPoints()
		origEnds = copy.deepcopy(endPoints)
		testVectors = copy.deepcopy(origTestVectors)
		curT = not curT 
		T = Ts[curT]



	if keys[pygame.K_c]:
		#curT = not curT
		curT = curT + 1 if curT != len(Ts)-1 else 0
		T = Ts[curT]
		print(T)
		time.sleep(.1)



	
