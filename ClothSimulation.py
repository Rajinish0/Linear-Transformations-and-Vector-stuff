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
## PLAY WITH THE VALUE OF GRAVITY..
gravity = 0.2

class Particle():
	def __init__(self, pos=None,pinned=False):
		self.pos = Vector(w//2+random.randint(-2,2),h//2+random.randint(-1,1)) if pos is None else pos
		## FOR INIT VELOCITY
		self.oldPos = Vector(self.pos.x+random.random()-7,self.pos.y) 
		# self.oldPos = copy.copy(self.pos)
		self.r = 3
		self.pinned = pinned

	def update(self):
		if not self.pinned:
			self.Edges()
			self.vel = (self.pos-self.oldPos)*.999
			self.oldPos = copy.copy(self.pos)
			self.pos += self.vel
			self.pos.y += gravity


	@property
	def x(self):
		return self.pos.x
	@property
	def y(self):
		return self.pos.y
	
	

	def render(self):
		pass
		# pygame.draw.circle(screen,(255,255,255),(self.pos.x,self.pos.y),self.r)

	def Edges(self):
		vel = self.pos - self.oldPos
		if self.pos.x> w:
			self.pos.x = w
			self.oldPos.x = self.pos.x + vel.x

		if self.pos.x< 0:
			self.pos.x = 0
			self.oldPos.x = self.pos.x + vel.x

		if self.pos.y> h:
			self.pos.y = h
			self.oldPos.y = self.pos.y + vel.y

		if self.pos.y< 0:
			self.pos.y = 0
			self.oldPos.y = self.pos.y + vel.y


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


class Stick():
	def __init__(self,p1,p2):
		self.p1 = p1
		self.p2 = p2
		self.length = dist(p1,p2)+2

	def fixEndpoints(self):
		dx = (self.p2.x - self.p1.x)
		dy = (self.p2.y - self.p1.y)
		disT = dist(self.p1,self.p2)
		offSet = (self.length-disT)/disT/2
		offSet = Vector(dx*offSet,dy*offSet)

		if not self.p1.pinned:
				self.p1.pos -= offSet
		if not self.p2.pinned:
				self.p2.pos += offSet

	def draw(self):
		self.fixEndpoints()
		pygame.draw.line(screen, (121,121,251), (self.p1.x,self.p1.y),(self.p2.x,self.p2.y),1)
def dist(p1,p2):
	return math.sqrt(pow(p1.x-p2.x,2)+pow(p1.y-p2.y,2))


def CheckEvent():
	global run, ps
	gotOrigPos = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			mousePosx = pygame.mouse.get_pos()[0]
			if mousePosx > w//2:
				ps[0][-1].pinned = not ps[0][-1].pinned
			else:
				ps[0][0].pinned = not ps[0][0].pinned

	keys = pygame.key.get_pressed()
	return (keys,run)

def GetMesh():
	global scl,angle,terrain
	vertices = []
	## THESE VALUES ARE AD HOC..
	for y in range(scl,h-300,20):
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
			sticks.append(Stick(a,b))
			sticks.append(Stick(a,c))
	return sticks

## A CHAINED CUBE

ps = [
Particle(Vector(w//2,h//2)),
Particle(Vector(w//2+40,h//2)),
Particle(Vector(w//2+40,h//2+40)),
Particle(Vector(w//2,h//2+40)),
PinnedParticle(Vector(w//2,h//2-70),100),
# Particle(Vector(w//2,h//2-70),pinned=False),
Particle(Vector(w//2,h//2-30)),
Particle(Vector(w//2,h//2-10)),
]

sticks = [
Stick(ps[4],ps[5]),
Stick(ps[5],ps[6]),
Stick(ps[6],ps[0]),
Stick(ps[0],ps[1]),
Stick(ps[1],ps[2]),
Stick(ps[2],ps[3]),
Stick(ps[0],ps[3]),
Stick(ps[0],ps[2]),
]



# ps = [Particle() for i in range(2)]
# sticks = [Stick(*ps)]

## CLOTH 
ps = GetMesh()
sticks = getSticks(ps)
ps[0][0].pinned = True
ps[0][-1].pinned = True

def func():
	screen.fill((0,0,0))
	[(p.update(), p.render()) for each in ps for p in each]
	[stick.draw() for stick in sticks]
	pygame.display.update()
	CheckEvent()

while run:
	func()
