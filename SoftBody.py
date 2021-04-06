## GOTTA IMPLEMENT COLLISION WITH POLYGONS
import pygame,random,math,time,copy,sys,threading, numpy as np
from seein import Vector, Matrix
from vf import DiffRootVector
from exp import Boid
run = True
w,h = 1200,600
alteredW = 1500
alteredH = 1500
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
scl = 30
deltaTime = .6
gravity =.1
sin,cos = math.sin,math.cos
rad = math.radians
randint = random.randint

class Particle():
	def __init__(self, pos=None,pinned=False):
		self.pos = Vector(w//2,h//2+200) if pos is None else pos
		self.vel = Vector(randint(-5,5),randint(-5,5)).normalized() * 50
		self.vel = Vector(0,0)
		self.acc = Vector(0,0)
		self.r = 3
		self.pinned = pinned
		self.friction = .999

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
		pygame.draw.circle(screen,(255,255,255),(self.pos.x,self.pos.y),self.r)

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

## UH THIS IS A SPRING..
class Stick():
	def __init__(self,p1,p2):
		self.p1 = p1
		self.p2 = p2
		self.length = dist(p1,p2)+2
		self.kr = .2  ## restoration constant or the dampening factor; same thing.
		self.ks = .4 ## SPRING CONSTANT

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
		pygame.draw.line(screen, (121,121,251), (self.p1.x,self.p1.y),(self.p2.x,self.p2.y),1)

def dist(p1,p2):
	return math.sqrt(pow(p1.x-p2.x,2)+pow(p1.y-p2.y,2))

sclsq = 10
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
	for y in range(scl+50,h-430,20):
		verts = []
		for x in range(w//2-100,w//2 + w-1100,20):
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
			sticks.append(Stick(a,b))
			sticks.append(Stick(a,c))
			sticks.append(Stick(a,d))
			sticks.append(Stick(b,c))

		sticks.append(Stick(Mesh[i][-1],Mesh[i+1][-1]))

	for i,each in enumerate(Mesh[-1][1:]):
		sticks.append(Stick(Mesh[-1][i],each))




	return sticks



ps = GetMesh()
sticks = getSticks(ps)
ps = [p for each in ps for p in each]

# [each.pos.rotate(Vector(w//2,h//2),45) for each in ps]
def func():
	global drawMode
	screen.fill((0,0,0))		
	[(p.update(), p.render()) for p in ps]		
	[stick.draw() for stick in sticks]		
	drill(ps)
	pygame.display.update()
	CheckEvent()

while run:
	func()
