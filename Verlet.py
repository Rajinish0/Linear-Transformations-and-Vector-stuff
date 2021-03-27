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
scale = 50
depth = 150 ## Z depth for three d plane


class Particle():
	def __init__(self, pos=None,pinned=False):
		self.pos = Vector(w//2+random.randint(-2,2),h//2+random.randint(-1,1)) if pos is None else pos
		self.oldPos = Vector(self.pos.x+random.random()-5,self.pos.y+random.random()-5)
		self.r = 3
		self.pinned = pinned

	def update(self):
		if not self.pinned:
			self.Edges()
			self.vel = (self.pos-self.oldPos)*.999
			self.oldPos = copy.copy(self.pos)
			self.pos += self.vel
			self.pos.y += .001


	@property
	def x(self):
		return self.pos.x
	@property
	def y(self):
		return self.pos.y
	
	

	def render(self):
		pygame.draw.circle(screen,(255,255,255),(self.pos.x,self.pos.y),self.r)

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
		self.angle += .001
		PinnedParticle.update = Particle.update if not self.pinned else PinnedParticle.update

	def render(self):
		pygame.draw.circle(screen, (0,0,255), (self.basePos.x,self.basePos.y),self.range,2)
		Particle.render(self)


class Stick():
	def __init__(self,p1,p2):
		self.p1 = p1
		self.p2 = p2
		print(p1,p2)
		self.length = dist(p1,p2)

	def fixEndpoints(self):
		dx = self.p2.x - self.p1.x
		dy = self.p2.y - self.p1.y
		disT = dist(self.p1,self.p2)
		offSet = (self.length-disT)/disT/2
		offSet = Vector(dx*offSet,dy*offSet)

		if not self.p1.pinned:
				self.p1.pos -= offSet
		if not self.p2.pinned:
				self.p2.pos += offSet

	def draw(self):
		self.fixEndpoints()
		pygame.draw.line(screen, (255,0,0), (self.p1.x,self.p1.y),(self.p2.x,self.p2.y),1)

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
			ps[4].pinned = not ps[4].pinned
			# print(ps[4].pinned)

	keys = pygame.key.get_pressed()
	return (keys,run)


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
def func():
	screen.fill((0,0,0))
	[(p.update(), p.render()) for p in ps]
	[stick.draw() for stick in sticks]
	pygame.display.update()
	CheckEvent()

while run:
	func()