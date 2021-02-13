import pygame,random,math,time,copy
from seein import Vector, Matrix
run = True
w,h = 900,480
clock = pygame.time.Clock()
screen = pygame.display.set_mode((w,h))
maxSpeed = 200
frameRate = 30
angleTurn = 10
angle = 0
deltaTime = 1/frameRate
orthographicProj = Matrix([[1,0,0],
						  [0,1,0]])

def GetCube():
	Vertices = [Vector(-50,-50,50),
				Vector(50,-50,50),
				Vector(50,50,50),
				Vector(-50,50,50),

				Vector(-50,-50,-50),
				Vector(50,-50,-50),
				Vector(50,50,-50),
				Vector(-50,50,-50),
				]
	for each in Vertices:
		each.x += 100				## JUST MESSING AROUND WITH THE CENTER
		each.y += 100
	return Vertices;
def CheckEvent():
	global run
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
	keys = pygame.key.get_pressed()
	return (keys,run)
def drawLine(v1,v2):
	x1,y1,x2,y2 = v1.x,v1.y,v2.x,v2.y
	wThresh,hThresh = w//2,h//2
	pygame.draw.line(screen,(0,255,0),(wThresh+x1,hThresh+y1),(wThresh+x2,hThresh+y2),2)
def DrawLines(vert):
	for i in range(4):
		drawLine(vert[i],vert[(i+1)%4])
		drawLine(vert[i+4],vert[((i+1)%4)+4])
		drawLine(vert[i],vert[i+4])

Cube = GetCube()
Center = Vector(100,100,0) 			#LOOKS PRETTY COOL with center = (0,0,0) too
while run:
	screen.fill((0,0,0))
	RotatedCube = [v.RotationX(angle,Center) for v in Cube]
	RotatedCube = [v.RotationZ(angle,Center) for v in RotatedCube]
	orthographicProjs = [Matrix([[(1+(.5-r.z/3)/100),0,0],						## NAIVE ATTEMPT TO MODEL PRESPECTIVE PROJECTIONS
						  [0,(1+(.5-r.z/3)/100),0]]) for r in RotatedCube]
	projs = [v.applyTransformation(orthographicProjs[i]) for i,v in enumerate(RotatedCube)]
	[pygame.draw.circle(screen,(255,255,255), (int(w//2+proj.x),int(h//2+proj.y)),4) for proj in projs]
	angle -= .2
	DrawLines(projs)
	pygame.display.update()
	keys, run = CheckEvent()
