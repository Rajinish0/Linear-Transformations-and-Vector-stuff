import pygame,random,math,time,copy,sys,threading, numpy as np
from pygame.locals import *
from seein import Vector, Matrix
from vf import DiffRootVector
from exp import Boid

class Particle():
	def __init__(self,pos=None):
		self.pos = Vector(random.randint(0,w), random.randint(0,h)) if pos is None else pos
		self.vel = Vector(random.randint(-200,200),random.randint(-200,200))*frameRate/40
		self.acc = Vector(0,0)
		self.r = 8
		self.c = (255,255,255)
	@property
	def x(self):
		return self.pos.x
	@property
	def y(self):
		return self.pos.y

	def update(self):
		self.edges()
		self.applyForce(Vector(0,100))
		self.pos += self.vel*deltaTime
		self.vel += self.acc*deltaTime
		self.acc = Vector(0,0)

	def show(self):
		self.update()
		drawCircle(self.pos,self.c, r=self.r)

	def applyForce(self, force):
		self.acc += force


	# def edges(self):
	# 	if self.pos.x+self.r > w:
	# 	    self.pos.x = w-self.r
	# 	    self.vel.x *= -1
	# 	if self.pos.x-self.r < 0:
	# 	    self.pos.x = self.r
	# 	    self.vel.x *= -1
	# 	if self.pos.y+self.r > h:
	# 	    self.pos.y = h-self.r
	# 	    self.vel.y *= -1
	# 	if self.pos.y-self.r < 0:
	# 	    self.pos.y = self.r
	# 	    self.vel.y *= -1
	

	def edges(self):
		v = self.vel.normalized()
		# m = v.y/v.x if v.x != 0 else float('inf')
		# b = v.y-m*v.x if v.x != 0 else float('inf')
		if self.pos.x+self.r > w:
		    self.pos.x = w-self.r
		    # self.pos.y = m*(self.pos.x)+b
		    self.vel.x *= -1
		if self.pos.x-self.r < 0:
		    self.pos.x = self.r
		    # self.pos.y = b
		    self.vel.x *= -1
		if self.pos.y+self.r > h:
		    self.pos.y = h-self.r
		    # self.pos.x = (self.pos.y-b)/m if self.vel.x != 0 else self.pos.x 
		    self.vel.y *= -1
		if self.pos.y-self.r < 0:
		    self.pos.y = self.r
		    # self.pos.x = (self.pos.y-b)/m if self.vel.x != 0 else self.pos.x
		    self.vel.y *= -1



class Box:
	particles = []
	def __init__(self,vertices, height, width,particleThreshold=5,parent= None,particles=[]):
		Box.particles = particles if particles != [] else Box.particles
		# global particleThreshold
		self.tl = vertices[0]
		self.height = height
		self.width = width
		self.pt = particleThreshold ## INCREASE THIS IN PROPORTION WIH TOTAL PARTICLES, BUILDING BOXES IS EXPENSIVE.
		self.c = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
		self.parent = parent
		self.checked = {}
		self.particlesInMe = {}
		self.children = self.GetChildren()


	def GetChildren(self):
		# global particles 
		particleCount = 0
		children = []
		for p in Box.particles:

			if self.parent is None or self.parent.checked.get(p):

					if self.particleInArea(p):
						particleCount += 1
						self.checked[p] = True

						self.particlesInMe[p] = 1


						if self.parent is not None:
							del self.parent.particlesInMe[p]


		if particleCount >= self.pt:
			nh, nw = self.height/2, self.width/2
			c1 = Box([self.tl],nh,nw,self.pt, self)
			c2 = Box([Vector(self.tl.x, self.tl.y + self.height/2)], nh, nw,self.pt, self)
			c3 = Box([Vector(self.tl.x + self.width/2, self.tl.y)], nh, nw,self.pt, self)
			c4 = Box([Vector(self.tl.x + self.width/2, self.tl.y+ self.height/2)], nh,nw,self.pt,self)

			children = [c1,c2,c3,c4]
			#verts = [self.tl/2, self.tr/2, self.bl, self.br]
			#verts = [self.tl/2, self.tr/2, self.bl, self.br]
		return children




	def drawBoundingBox(self):
		x,y =self.tl.x,self.tl.y
		rect = Rect(x,y,(self.width), (self.height))
		pygame.draw.rect(screen,(81,81,181),rect,1)

	def particleInArea(self, particle):
		minx, miny, maxX, maxY = self.tl.x, self.tl.y, self.tl.x + self.width, self.tl.y + self.height
		x,y = particle.x, particle.y
		return (minx<x<maxX and miny<y<maxY)

	def show(self):
		self.drawBoundingBox()
		for each in self.children:
			each.show()

	def printParticles(self):
		s = 0
		# for p in self.particlesInMe:
			# p.c = self.c

		for each in self.children:
			s += each.printParticles()
		s += len(self.particlesInMe)
		return s

	def CheckCollisions(self):
		l = list(self.particlesInMe.keys())
		for i,p in enumerate(l[:-1]):
			for another in l[i+1:]:
				if dist(p,another) < 2*p.r:
					reverseVelocities(p,another)
					# print(p.pos, another.pos)

		for each in self.children:
			each.CheckCollisions()

def dist(p1,p2):
	return math.sqrt(pow(p1.x-p2.x,2)+pow(p1.y-p2.y,2))

def reverseVelocities(p1,p2):
	# z = copy.deepcopy(p1.vel)

	mag = p1.vel.GetMagnitude()
	b1 = p2 if mag > 0 else p1
	b2 = p1 if mag > 0 else p2


	N = (b1.pos-b2.pos)
	v = b2.vel.normalized()
	proj = v*N.dot(v)
	tD = (proj-N).GetMagnitude()
	d = pow((b1.r+b2.r)**2-tD**2,.5)
	b2.pos = b2.pos + proj-v*d;


	N = (b1.pos-b2.pos).normalized()

	T = Vector(-N.y, N.x)
	v1n = b1.vel.dot(N)
	v2n = b2.vel.dot(N)
	v1t = b1.vel.dot(T)
	v2t = b2.vel.dot(T)

	b1.vel = N*(v2n) + T*(v1t)
	b2.vel = N*(v1n) + T*(v2t)




	# N = (p1.pos-p2.pos)
	# v = p1.vel.normalized()
	# v = v if v.GetMagnitude() > 0 else p2.vel.normalized()
	# proj = v*N.dot(v)
	# tD = (proj-N).GetMagnitude()
	# d = pow((p1.r+p2.r)**2-tD**2,.5)
	# p2.pos = p2.pos + proj-v*d;


	# N = (p1.pos-p2.pos).normalized()


	# # mag = N.GetMagnitude()
	# # dist = 2*p1.r-mag
	# # p1.pos = p1.pos+(N/mag)*(dist/2)#+(N/mag)*(1/2)
	# # p2.pos = p2.pos-(N/mag)*(dist/2)#-(N/mag)*(1/2)
	# # N = N/mag
	# # N = (p1.pos-p2.pos)/(2*p1.r+1)
	# # print('n2', N)

	# T = Vector(-N.y, N.x)
	# v1n = p1.vel.dot(N)
	# v2n = p2.vel.dot(N)
	# v1t = p1.vel.dot(T)
	# v2t = p2.vel.dot(T)

	# p1.vel = N*(v2n) + T*(v1t)
	# p2.vel = N*(v1n) + T*(v2t)

	# N = p1.pos-p2.pos
	# mag = N.GetMagnitude()
	# dist = 2*p1.r-mag
	# p1.pos = p1.pos+(N/mag)*(dist/2)#+(N/mag)*(1/2)
	# p2.pos = p2.pos-(N/mag)*(dist/2)#-(N/mag)*(1/2)
	# v1 = Vector(*p1.vel.elems[:])
	# v2 = Vector(*p2.vel.elems[:])
	# p1.vel = v1 - ((v1-v2).dot(N)/(mag**2))*N
	# p2.vel = v2 - ((v2-v1).dot(-N)/(mag**2))*(-N)


def CheckEvent():
	global run, ang, mouseIsDown, origXPos, origYPos,disT
	gotOrigPos = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			particles.append(Particle(Vector(*pygame.mouse.get_pos())))

	keys = pygame.key.get_pressed()
	return (keys,run)

def drawCircle(pos,c,r=4):
	pygame.draw.circle(screen,c,(pos.x,pos.y),r)

def CheckCollisions():
	global particles
	for i,p in enumerate(particles[:-1]):
		for another in particles[i+1:]:
			if dist(p,another) < p.r*2:
				reverseVelocities(p,another)


if __name__ == '__main__':
	run = True
	w,h = 1200,600
	alteredW = 1500
	alteredH = 1500
	screen = pygame.display.set_mode((w,h))
	clock = pygame.time.Clock()
	frameRate = 120
	deltaTime = 1/frameRate


	totalParticles =250
	particleThreshold = int(math.sqrt(totalParticles))
	particles = [Particle() for i in range(totalParticles)]
	b = Box([Vector(0,0)], h, w, particleThreshold,particles=particles)
	print(b.printParticles())
	def func():
		clock.tick(frameRate)
		screen.fill((0,0,0))
		[p.show() for p in particles]
		# CheckCollisions()
		b = Box([Vector(0,0)], h, w)
		# b.show()
		b.CheckCollisions()
		pygame.display.update()
		CheckEvent()

	while run:
		func()
 