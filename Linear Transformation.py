import pygame,random,math,time,copy,sys,threading
from seein import Vector, Matrix
from vf import DiffRootVector
run = True
w,h = 800,600
alteredW = 1500
alteredH = 1500
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
scale = 50
depth = 150 ## Z depth for three d octant

def CheckEvent():
	global run
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
			sys.exit()
	keys = pygame.key.get_pressed()
	return (keys,run)

def GetBasisVectors():
	global endPoints
	v1 = endPoints[0][0]
	v2 = endPoints[1][0]

	v3 = endPoints[-2][0]
	v4 = endPoints[-1][0]
	threshold = Vector(w//2,h//2)

	# return (v2-v1), (v4-v3)
	# if not ProjectIn3d:
	x1 = v2-v1
	x2 = v4-v3
	# else:
	# 	# v1,v2,v3,v4 = Get3dProjected(v1),Get3dProjected(v2),Get3dProjected(v3),Get3dProjected(v4)
	# 	#sprint(v1,v2)
	# 	x1,x2= v2-v1, v4-v3
	# 	print(x1)
	# 	# x1 = Get3dProjected(x1)
	# 	# x2= Get3dProjected(x2)
	# 	pygame.draw.line(screen,(255,255,255),(w//2+v1.x,h//2+v1.y),(w//2+v2.x,h//2+v2.y),5)
	# 	#print(v2-v1)

	ihat = DiffRootVector(threshold,*(x1),clampMagnitude=False)
	jhat = DiffRootVector(threshold,*(x2),clampMagnitude=False)
	return (ihat,jhat)
	

def drawBasisVectors():
	global ProjectIn3d,testVector
	if not ProjectIn3d:
		i,j = GetBasisVectors()
		for bVectors in (i,j):
			bVectors.b, bVectors.r,bVectors.g = (255,255,255)
			bVectors.draw(screen)
		if testVector is not None:
			vToTest = DiffRootVector(Vector(w//2,h//2),*testVector,clampMagnitude=False)
			vToTest.b,vToTest.r,vToTest.g = (0,255,0)
			vToTest.draw(screen)
			# pygame.draw.line(screen,(255,0,0),(w//2,h//2),(w//2+bVectors.x,h//2+bVectors.y),2)


def EndPoints():
	global threeDoctant
	# for z in range(0,depth,scale):
	print(threeDoctant)
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
	for z in range(0,150,scale):
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

def projg(vert):
	vert.x *= (1-(5-vert.z/25)/100)
	vert.y *= (1-(5-vert.z/25)/100)

ang = 1
def Get3dProjected(v):
	global ang,depth
	try:
		if v.z == 0:
			raise Exception()
		z = constrain(v.z,depth,25)
	except:
		z = constrain(v.y,alteredH,25)

	rotatedV = Vector(*v.elems[:2],z).RotationX(45,Vector(0,0,0))
	# print(ang)
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
	global origEnds,origTestVector
	screen.fill((0,0,0))

	try:
		DrawLines(origEnds,(21,21,51))
		if not ProjectIn3d:
			vToTest = DiffRootVector(Vector(w//2,h//2),*origTestVector,clampMagnitude=False)
			vToTest.b,vToTest.r = (51,51)
			vToTest.draw(screen)
	except:
		pass
	for i,func in enumerate(funcsToCall):
		func(*Args[i])

	pygame.display.update()
	CheckEvent()

def doTheRotation(v1,v2,angle):
	(v1.rotate(Vector(0,0),angle),v2.rotate(Vector(0,0),angle))		


def Lerp(a,b,percent):
	return (a+(b-a)*percent)

def adjustTransformation(T):
	origTrans = copy.deepcopy(T.mat)
	origTrans[1].x *= -1
	origTrans[0].y *= -1
	return Matrix(origTrans)

def applyTrans():
	global endPoints, T,testVector, threeDoctant
	percent = 0
	percentInc = .01 if not threeDoctant else .1
	IdentityMatrix = Matrix([[1,0],
							[0,1]])
	if threeDoctant:
		IdentityMatrix = Matrix([[1,0,0],
								[0,1,0],
								[0,0,1]])
	origVs = copy.deepcopy(endPoints)
	origTest = copy.copy(testVector)
	Transformation = adjustTransformation(T) if not threeDoctant else T

	while percent<=1:
		curTransformation = Lerp(IdentityMatrix,Transformation,percent)
		for i,(v1,v2) in enumerate(endPoints):
			endPoints[i] = (v1.applyTransformation(curTransformation),v2.applyTransformation(curTransformation))


		if testVector != None:
			testVector = testVector.applyTransformation(curTransformation)

		func([DrawLines,clock.tick,drawBasisVectors],Args=[
							[endPoints,(51,81,121)],
								[20],
								[]
								 ])
		percent += percentInc
		percent = round(percent,2)
		endPoints = copy.deepcopy(origVs) if not percent>1 else endPoints
		testVector = copy.copy(origTest) if not percent>1 else testVector


## SO YOU CAN PROJECT A 2d plane in 3d
ProjectIn3d = False

## OR YOU CAN HAVE A 3D PLANE
threeDoctant = True
if threeDoctant:
	ProjectIn3d = 1;

if ProjectIn3d:
	alteredW,alteredH = 700,700




endPoints = EndPoints()
origEnds = copy.deepcopy(endPoints)
#testVector=Vector(.55,-.83)*scale
#testVector=Vector(0,0)*scale
testVector = Vector(3,2)*scale ##y coord flipped
origTestVector = copy.copy(testVector)
Ts = {0:Matrix([[1,5], 
			[-1,-2]]),1:Matrix([[1,-1],
					[8,-2]])}
# Ts = {0:Matrix([[1,-1],
# 				[1,-1]]),1:Matrix([[-1,0],
# 								[0,1]])}
Ts = {0:Vector(0,0,0).RotationOnX(90), 1:Matrix([[1,-1,0],
				[1,2,0],
				[0,0,0]])}
curT = 0
T= Ts[curT]

if threeDoctant:
	assert (len(T.mat[0]) == 3)


while run:
	func([DrawLines,drawBasisVectors],Args=[
						  [endPoints,(51,81,121)],
						  []
						  ])
	keys = pygame.key.get_pressed()
	if keys[pygame.K_a]:
			applyTrans()
	if keys[pygame.K_r]:
		endPoints = EndPoints()
		origEnds = copy.deepcopy(endPoints)
		testVector = Vector(3,2)*scale
		origTestVector = copy.copy(testVector)
		curT = not curT 
		T = Ts[curT]


	if keys[pygame.K_c]:
		curT = not curT
		T = Ts[curT]
		print(T)
		time.sleep(.1)

	
