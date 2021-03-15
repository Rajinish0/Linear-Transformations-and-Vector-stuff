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
	global ProjectIn3d
	if not ProjectIn3d:
		i,j = GetBasisVectors()
		for bVectors in (i,j):
			bVectors.b, bVectors.r = (0,255)
			bVectors.draw(screen)
			# pygame.draw.line(screen,(255,0,0),(w//2,h//2),(w//2+bVectors.x,h//2+bVectors.y),2)

def EndPoints():
	global scale
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

def constrain(cur,total,maximum):
    return ((cur*abs(maximum)*2)/total)-maximum

def projg(vert):
	vert.x *= (1-(5-vert.z/25)/100)
	vert.y *= (1-(5-vert.z/25)/100)

def Get3dProjected(v):
	z = constrain(v.y,alteredH,25)
	rotatedV = Vector(*v.elems,z).RotationX(60,Vector(0,0,0))
	projg(rotatedV)
	return rotatedV

def DrawLines(l,c):
	global ProjectIn3d

	for i,(v1,v2) in enumerate(l):
		x1,y1,x2,y2 = v1.elems+v2.elems
		## 3D projected Rotation of the 2d plance
		if ProjectIn3d:
			nV1 = Get3dProjected(v1)
			nV2 = Get3dProjected(v2)
			pygame.draw.line(screen,c,(nV1.x+w//2,nV1.y+h//2),(nV2.x+w//2,nV2.y+h//2),2)
		else:
			pygame.draw.line(screen,c,(x1+w//2,y1+h//2),(x2+w//2,y2+h//2),2)


def func(funcsToCall=[], Args=None):
	screen.fill((0,0,0))
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
	global endPoints, T
	percent = .1
	IdentityMatrix = Matrix([[1,0],
							[0,1]])
	origVs = copy.deepcopy(endPoints)
	Transformation = adjustTransformation(T)
	while percent<=1:
		curTransformation = Lerp(IdentityMatrix,Transformation,percent)
		for i,(v1,v2) in enumerate(endPoints):
			endPoints[i] = (v1.applyTransformation(curTransformation),v2.applyTransformation(curTransformation))
		func([DrawLines,clock.tick,drawBasisVectors],Args=[
							[endPoints,(51,81,121)],
								[20],
								[]
								 ])
		percent += 0.01
		percent = round(percent,2)
		print(curTransformation,percent)
		endPoints = copy.deepcopy(origVs) if not percent>1 else endPoints


ProjectIn3d = False
endPoints = EndPoints()
T = Matrix([[1,1],
			[1,1]])

print(adjustTransformation(T))
done = False

while run:
	func([DrawLines,drawBasisVectors],Args=[
						  [endPoints,(51,81,121)],
						  []
						  ])
	keys = pygame.key.get_pressed()
	if keys[pygame.K_a]:
			applyTrans()
			done = not done

	
