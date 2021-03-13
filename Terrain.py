import pygame,random,math,time,copy,sys,noise
from Linalg import Vector, Matrix
run = True
w,h = 1000,680
alteredW = 1200								## multiple of scl, for safe measures.
alteredH = 1500
clock = pygame.time.Clock()
screen = pygame.display.set_mode((w,h))
maxSpeed = 200
frameRate = 30
angleTurn = 10
scl = 30
flying = 0
deltaTime = 1/frameRate
orthographicProj = Matrix([[1,0,0],
			   [0,1,0]])


def CheckEvent():
	global run
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
	keys = pygame.key.get_pressed()
	return (keys,run)

def drawLine(v1,v2, c= (255,0,0)):
	x1,y1,x2,y2 = v1.x,v1.y,v2.x,v2.y
	wThresh,hThresh = w//2,h//2
	pygame.draw.line(screen,c,(wThresh+x1,hThresh+y1),(wThresh+x2,hThresh+y2),2)


## MAPS (-1,1) to a maximum limit so cur=-1 yeilds -maximum, 0 yields 0, 1 yeilds maximum, you get the idea
def constrain(cur,maximum):
    return (((cur+1)*abs(maximum)*2)/2)-maximum

def GetRandomZVals():
	global flying
	terrain = []
	yOff = copy.copy(flying)
	for y in range(-alteredH//2,alteredH//2,scl*2):
		t = []
		xOff =0
		for x in range((-alteredW//2),alteredW//2,scl):
			rNoise = noise.pnoise2(xOff,yOff)
			rNoise= constrain(rNoise,200)
			t.append(rNoise)
			xOff += .1
		terrain.append(t)
		yOff += .1
	flying -= .1
	return terrain

def GetVertices(pos,r,shape='SQUARE',z=0):
	if shape == 'TRIANGLE':
			topVertex = Vector(pos.x+r,pos.y,z)
			bottomLeft = Vector(pos.x-r,pos.y-r,z)
			bottomRight = Vector(pos.x-r,pos.y+r,z)
			return [topVertex,bottomLeft,bottomRight]
	elif shape == 'SQUARE':
			topLeft = Vector(pos.x-r,pos.y+r,z)
			topRight = Vector(pos.x+r,pos.y+r,z)
			bottomLeft = Vector(pos.x-r,pos.y-r,z)
			bottomRight = Vector(pos.x+r,pos.y-r,z)
			return [topLeft,topRight,bottomRight,bottomLeft]
	else:
		raise Exception(shape + ' is invalid, puta.');
def GetMesh():
	global scl,angle,terrain
	vertices = []
	j = 0
	for y in range(-alteredH//2,alteredH//2,scl*2):
		i = 0
		for x in range((-alteredW//2),alteredW//2,scl):
			verts = [Vector(x,y,terrain[j][i]), Vector(x,y+scl,terrain[j][i])]
			verts = [each.RotationX(60,Vector(0,0,0),return_new= False) for each in verts]
			'''try random values, by all means.'''
			orthographicProjs = [Matrix([[(1-(5-r.z/10)/100),0,0],
						[0,(1-(5-r.z/10)/100),0]]) for r in verts]
			verts = [each.applyTransformation(orthographicProjs[i]) for i,each in enumerate(verts)]
			vertices.append(verts)
			i += 1
		j += 1
	return vertices

def DrawPiece(vertices):
	c = (51,81,51)
	for i,vert in enumerate(vertices):
		drawLine(vertices[i-1],vert,c)
	drawLine(vertices[0],vertices[-1],c)
	drawLine(vertices[1],vertices[3],c) ## DIAGONAL

def DrawMesh(Mesh):
	for ind,vertices in enumerate(Mesh):
		#VERY MESSY.
		if ind % (alteredW//scl) != 0: 
			DrawPiece(vertices+Mesh[ind-1][::-1])
			if ind > alteredW//scl:
				nVert = [Mesh[(ind-(alteredW//scl))][1],vertices[0],Mesh[ind-1][0],Mesh[(ind-(alteredW//scl))-1][1]]
				DrawPiece(nVert)


		
angle = .2

## COPY THESE DOWN OVER DRAWMESH to sort of fly over the terrain at 2 frames per second ;-;, gotta optimizie.
terrain = GetRandomZVals()
Mesh = GetMesh()

while run:
	screen.fill((0,0,0))
	DrawMesh(Mesh)
	pygame.display.update()
	keys, run = CheckEvent()
