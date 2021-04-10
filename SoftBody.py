## soft body simulation
## used raycasting for object detection
## 2 rays are used, one's parallel to the x axis and has the euqation y= y0 where y0's the y coordinate of the particle
## another's x = x0 --> x coord of the particle.

##If any one the rays collide with an even number of sides of the polygon, the particle gets deflected
## the rays are ofc used to calculate which is the nearest point of deflection, the force nearestpoint - self.pos is perpendicular to the side of the shape.

import pygame,random,math,time,copy,sys, numpy as np
from Linalg import Vector, Matrix
from vf import DiffRootVector
from exp import Boid
from pygame.locals import *
run = True
w,h = 1200,600
alteredW = 1500
alteredH = 1500
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
scl = 30
deltaTime = .6
gravity =.08
sin,cos = math.sin,math.cos
rad = math.radians
randint = random.randint

class Particle():
	def __init__(self, pos=None,pinned=False):
		self.pos = Vector(w//2,h//2+200) if pos is None else pos
		# self.vel = Vector(randint(-5,5),randint(-5,5)).normalized() * 50
		self.vel = Vector(0,0)
		self.acc = Vector(0,0)
		self.r = 3
		self.pinned = pinned
		self.friction = .99

	def update(self):
		if not self.pinned:
			self.Edges()
			self.applyForce(Vector(0,gravity))
			self.vel += (self.acc*deltaTime)*self.friction
			self.pos += self.vel*deltaTime
			self.acc = Vector(0,0)


	@property
	def x(self):
		return self.pos.x
	@property
	def y(self):
		return self.pos.y
	
	

	def applyForce(self,f):
		self.acc += f
	def render(self):
		pass
		# pygame.draw.circle(screen,(255,255,255),(self.pos.x,self.pos.y),self.r)

	def Edges(self):
		if self.pos.x> w-5:
			p = Vector(w-5,copy.copy(self.pos.y))
			self.applyForce(p-self.pos)

		if self.pos.x< 5:
			p = Vector(5,copy.copy(self.pos.y))
			self.applyForce(p-self.pos)		

		if self.pos.y> h-5:
			p = Vector(copy.copy(self.pos.x),h-5)
			self.applyForce(p-self.pos)

		if self.pos.y< 5:
			p = Vector(copy.copy(self.pos.x),5)
			self.applyForce(p-self.pos)

	def collisionHandling(self, poly):
		bounds = poly.bounds
		hasCollided = False
		nearest = None
		minDist = float('inf')
		collidedWith = 0

		for each in bounds:
			c1 = collisionPoint((self.x,self.y),each, isHorizontal= False)
			c2 = collisionPoint((self.x,self.y),each)
			if c2 != None and c2[0] < self.x:
				collidedWith += 1

			nearest, minDist = setNearest(c1, self.pos, nearest, minDist)
			nearest, minDist = setNearest(c2, self.pos, nearest, minDist)

		if not collidedWith % 2 == 0:
			# pygame.draw.circle(screen,(255,0,255),(nearest.x,nearest.y),5)
			self.applyForce((nearest-self.pos)*2)


def setNearest(v1,v2, nearest, minDist):
	if v1 != None:
		v1 = Vector(*v1)
		d = dist(v1,v2,sqr=True)
		if d < minDist:
			nearest = v1
			minDist = d
	return (nearest, minDist)

def collisionPoint(coord, bound, isHorizontal=True):
	px, py = coord
	if not isHorizontal:
		x = px
		y = bound.m*(x) + bound.b if bound.m != None else None
		if bound.m == None:
			if abs(bound.x1-x) < .01:
				y = py
	else:
		y = py
		x = (y-bound.b)/bound.m if (bound.m != 0 and bound.m != None) else None
		if bound.m is None:
			x = bound.x1
			
	if x != None and y!= None:		
		if min(bound.x1,bound.x2)<=x<=max(bound.x1,bound.x2) and min(bound.y1,bound.y2)<=y<=max(bound.y1,bound.y2):
			return (x,y)
	return None

class PinnedParticle(Particle):
	def __init__(self,basePos,range_,rect=True):
		super().__init__()
		self.basePos = basePos
		self.pos = copy.deepcopy(self.basePos)
		self.range = range_
		self.r = 3
		self.rect = rect
		self.angle = 0
		self.pinned = True



	def update(self):
		self.pos.x = self.basePos.x +  self.range*(math.cos(self.angle))
		self.pos.y = self.basePos.y + self.range*(math.sin(self.angle))
		self.angle += .005
		PinnedParticle.update = Particle.update if not self.pinned else PinnedParticle.update

	def render(self):
		pygame.draw.circle(screen, (0,0,255), (self.basePos.x,self.basePos.y),self.range,2)
		Particle.render(self)

## I should probably rename this to spring
class Stick():
	def __init__(self,p1,p2):
		self.p1 = p1
		self.p2 = p2
		self.length = dist(p1,p2)+2
		self.kr = .2  ## restoration constant or the dampening factor; same thing.
		self.ks = .7 ## SPRING CONSTANT
		self.hidden = False

	def fixEndpoints(self):

		f1 = (self.p1.pos - self.p2.pos)
		damp = self.p1.vel
		mag = f1.GetMagnitude()
		f1= f1/mag

		d1 = (self.p1.vel - self.p2.vel)
		d1 = d1.dot(-1*f1) * self.kr
		ft = (mag-self.length)*self.ks-d1

		f1 *= ft
		f2 = -1* f1

		self.p1.applyForce(f2)
		self.p2.applyForce(f1)

	def draw(self):
		self.fixEndpoints()
		if not self.hidden:
				pygame.draw.line(screen, (121,121,251), (self.p1.x,self.p1.y),(self.p2.x,self.p2.y),1)

def dist(p1,p2,sqr=False):
	d = pow(p1.x-p2.x,2)+pow(p1.y-p2.y,2)
	return math.sqrt(d) if not sqr else d


class Polygon:
	def __init__(self,vertices):
		self.vertices = vertices
		self.BoundingBox = self.getBoundingBox()
		self.bounds = self.getBounds()

	def getBoundingBox(self):
		
		(minx, miny, maxX, maxY) = (float('inf'), float('inf'), float('-inf'), float('-inf'))
		
		for each in self.vertices:
			minx, miny, maxX, maxY = min(minx,each.x), min(miny,each.y), max(maxX,each.x), max(maxY,each.y)
			
		return {'minx':minx,
				'miny':miny,
				'maxX':maxX,
				'maxY':maxY
		}

	def drawBoundingBox(self):
		x,y =self.BoundingBox['minx'], self.BoundingBox['miny']
		rect = Rect(x,y,(self.BoundingBox['maxX'] - self.BoundingBox['minx']), (self.BoundingBox['maxY'] - self.BoundingBox['miny']))
		pygame.draw.rect(screen,(255,255,255),rect,2)

	def getBounds(self):
		bounds = []
		for i, each in enumerate(self.vertices[:-1]):
			bounds.append(Ray(each, self.vertices[i+1]))
		bounds.append(Ray(self.vertices[0],self.vertices[-1]))
		return bounds

	def particleInArea(self, particle):
		minx, miny, maxX, maxY = list(self.BoundingBox.values())
		x,y = particle.x, particle.y
		return (minx<x<maxX and miny<y<maxY)

	def show(self):
		for each in self.bounds:
			each.draw()


class Ray():
	def __init__(self,v1,v2):
		self.v1 = v1
		self.v2 = v2	
		self.x1,self.y1,self.x2,self.y2 = self.v1.x,self.v1.y,self.v2.x,self.v2.y
		self.calc()

	def calc(self):
		self.m = (self.y2-self.y1)/(self.x2-self.x1) if (self.x1 != self.x2) else None
		if self.m != 0:
			self.b = self.y1-(self.m*self.x1) if (self.m != None) else None
		else:
			self.b = self.y1

	def draw(self):
		pygame.draw.line(screen, (255,0,0),(self.x1,self.y1),(self.x2,self.y2),2)



sclsq = 8
def drill(ps):
	global sclsq
	disgust = 2
	for i,each in enumerate(ps):
		for oth in ps[i+1:]:
			d = dist(each,oth) 
			if d < sclsq:
				f = (disgust)*(each.pos-oth.pos)
				each.applyForce(f)
				oth.applyForce(-1*f)


def CheckEvent():
	global run, ps,sticks
	gotOrigPos = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			mousePosx = pygame.mouse.get_pos()[0]
			ps[0].pinned = not ps[0].pinned

	keys = pygame.key.get_pressed()
	return (keys,run)


ps = [
Particle(Vector(w//2,h//2)),
Particle(Vector(w//2+40,h//2)),
Particle(Vector(w//2+40,h//2+40)),
Particle(Vector(w//2,h//2+40)),
PinnedParticle(Vector(w//2,h//2-70),100),
Particle(Vector(w//2,h//2-60)),
Particle(Vector(w//2,h//2-50)),
Particle(Vector(w//2,h//2-40)),
Particle(Vector(w//2,h//2-30)),
Particle(Vector(w//2,h//2-10)),
]

sticks = [
Stick(ps[0],ps[1]),
Stick(ps[1],ps[2]),
Stick(ps[2],ps[3]),
Stick(ps[0],ps[3]),
Stick(ps[0],ps[2]),
Stick(ps[4],ps[5]),
Stick(ps[5],ps[6]),
Stick(ps[6],ps[7]),
Stick(ps[7],ps[8]),
Stick(ps[8],ps[9]),
Stick(ps[0],ps[9]),
Stick(ps[1],ps[3])

]


def GetMesh():
	global scl,angle,terrain
	vertices = []
	for y in range(scl+50,h-450,15):
		verts = []
		for x in range(w//2-100,w//2 + w-1130,15):
			verts.append(Particle(Vector(x,y)))
		vertices.append(verts)
	return vertices


def getSticks(Mesh):
	sticks = []
	for i in range(len(Mesh)-1):
		for j in range(len(Mesh[0])-1):
			a = Mesh[i][j]
			b = Mesh[i+1][j]
			c = Mesh[i][j+1]
			d = Mesh[i+1][j+1]

			s1 =Stick(a,b)
			s2 =Stick(a,c)
			s3 =Stick(a,d)
			s4 =Stick(b,c)
			sticks.append(s1)
			sticks.append(s2)
			sticks.append(s3)
			sticks.append(s4)

			# s1.hidden = True
			# s2.hidden = True
			# s3.hidden = True
			# s4.hidden = True
			# if i < 1:
				# s2.hidden = False

			# if j < 1:
				# s1.hidden = False


		sticks.append(Stick(Mesh[i][-1],Mesh[i+1][-1]))

	for i,each in enumerate(Mesh[-1][1:]):
		sticks.append(Stick(Mesh[-1][i],each))




	return sticks




ps = GetMesh()
sticks = getSticks(ps)
ps = [p for each in ps for p in each]
verts = [Vector(w//2-20,h//2), Vector(w//2-20,h//2 - 100), Vector((w//2)+100,h//2 - 50), Vector((w//2 + 200), h//2-50)]


verts_ = [Vector(w//2-100,h//2 +100), Vector(w//2 - 100,h//2 + 200), Vector((w//2),h//2 + 200), Vector((w//2), h//2+100)]
verts_ = [each-Vector(370,0) for each in verts_]

verts__ = [Vector(w//2-100,h//2 +100), Vector(w//2 - 100,h//2 + 200), Vector((w//2),h//2 + 200), Vector((w//2), h//2+120), Vector(w//2+250, h//2)]
verts__ = [each-Vector(200,0) for each in verts__]

pols = [Polygon(verts), Polygon(verts_),Polygon(verts__)]


def func():
	global drawMode
	screen.fill((0,0,0))	
	[(pol.show())	for pol in pols]
	for each in ps:
		for pol in pols:
				if pol.particleInArea(each):
						each.collisionHandling(pol)
	[(p.update(), p.render()) for p in ps]		
	[stick.draw() for stick in sticks]		
	drill(ps)
	pygame.display.update()
	CheckEvent()

while run:
	func()
