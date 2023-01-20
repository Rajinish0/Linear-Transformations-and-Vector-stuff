##trajectory calculation in 8 ball pool

import pygame,random,math,time,copy,sys,threading, numpy as np
from pygame.locals import *
from Linalg import Vector, Matrix
from coloptimization import *

run = True
w,h = 800,600
alteredW = 1500
alteredH = 1500
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
frameRate = 240
deltaTime = 1/frameRate
mousePressed, mouseReleased, mouseJustPressed = (False,)*3
def drawCircle(v,c=(255,255,255), r=2, thick=0):
	pygame.draw.circle(screen, c, (v.x,v.y), r, thick)

def drawLine(v1,v2,c=(255,255,255),thick=2):
	pygame.draw.line(screen, c, (v1.x, v1.y),
								(v2.x, v2.y))

def checkForCollisionWithHoles(pos, r, holes):
	for hole in holes:
		if Hole.isIn(pos, hole.pos, r, hole.r):
			return (True, hole.pos)
	return (False, None)


def Trace(pos, uhat,r, balls, holes, depth=6, draw=True, wallRic=False):
	global do
	collided, holePos = checkForCollisionWithHoles(pos, r, holes)
	# print(collided)
	if collided:
		return (collided, holePos, uhat)

	if depth <= 0: #and (not wallRic or depth < -10):
		return (False, pos, uhat)
	minDist = float('inf')
	nearestBall = None
	tD = 0
	projD = None
	for ball in balls:
		vec = (ball.pos-pos)
		dot = vec.dot(uhat)
		if dot < 0:
			continue
		proj = uhat*(dot)
		tangentialDistance = (vec - proj).GetMagnitude()
		if 0<tangentialDistance <= (r+ball.r):
			p = dist(pos, ball)
			if p < minDist:
				minDist = p;
				nearestBall = ball;
				tD = tangentialDistance
				projD = proj


	if nearestBall is not None:
		d = pow((r+nearestBall.r)**2 - tD**2, .5)
		center = projD-uhat*d
		newCenter = pos+center
		vec = (nearestBall.pos - pos-center)
		vec90 = Vector(-vec.y, vec.x)

		if draw:
			drawCircle(pos + center, r=r, thick=1)
			drawLine(pos, pos+center, c=(0, 255, 0))
			drawLine(pos+center, pos+center+vec*2, c= (0, 0, 255))
			drawLine(pos+center, pos+center+vec90*2, c=(0,0,255))
		return Trace(pos+center+vec, vec.normalized(),r, balls, holes, depth-1, draw, wallRic=False)

	else:
		m,b = ((uhat.y)/(uhat.x), pos.y-(uhat.y/uhat.x)*pos.x) if uhat.x != 0 else (None,)*2

		ps = [(Vector((w-r), m*(w-r) + b) if uhat.x != 0 else None), 
			  (Vector((r), m*(r) + b) if uhat.x != 0 else None),
			  (Vector((h-r-b)/m ,h-r) if (uhat.x != 0 and uhat.y!=0) else Vector(pos.x, h) if uhat.y != 0 else None), 
			  (Vector((r-b)/m, r) if (uhat.x != 0 and uhat.y!=0) else Vector(pos.x, 0) if uhat.y != 0 else None)]
		nP = None
		minD = float('inf')


		for i in range(4):
			if ps[i] is None or (ps[i]-pos).dot(uhat) < 0:
				continue
			d = dist(pos, ps[i])
			if d < minD and d!= 0:
				minD = d;
				nP = i

		try:
			center = ps[nP]
		except Exception as err:
			return (False, pos, uhat) # (None,)*3

		
		newUhat = Vector(-uhat.x, uhat.y) if nP == 0 or nP == 1 else Vector(uhat.x, -uhat.y)

		if draw:
			drawCircle(center, r= r, thick=1)
			drawLine(pos, center, c=(0, 255, 0))
			drawLine(center, center + newUhat*r*2, c= (0, 0, 255))
		return Trace(center, newUhat,r, balls,holes, depth-1, draw, wallRic=True)



class Particle():
	def __init__(self,pos=None,vel=Vector(0,0), r=None, c=None, randomVel=False):
		self.pos = pos or Vector(random.randint(0,w), random.randint(0,h))
		self.vel = vel if not randomVel else Vector(random.randint(-200,200),random.randint(-200,200))*frameRate/40
		self.acc = Vector(0,0)
		self.r = r or 10
		self.c = c or (255,0,0)
	@property
	def x(self):
		return self.pos.x
	@property
	def y(self):
		return self.pos.y

	def update(self):
		self.edges()
		# self.applyForce(Vector(0,100))
		self.pos += self.vel*deltaTime
		self.vel += self.acc*deltaTime
		self.vel *= .995
		self.show()
		self.acc = Vector(0,0)

	def show(self):
		drawCircle(self.pos,self.c, r=self.r)
		drawLine(self.pos, self.pos+self.vel.normalized()*self.r*2, c= (255, 0, 255))

	def applyForce(self, force):
		self.acc += force


	def edges(self):
		if self.pos.x+self.r > w:
		    self.pos.x = w-self.r
		    self.vel.x *= -1
		if self.pos.x-self.r < 0:
		    self.pos.x = self.r
		    self.vel.x *= -1
		if self.pos.y+self.r > h:
		    self.pos.y = h-self.r 
		    self.vel.y *= -1
		if self.pos.y-self.r < 0:
		    self.pos.y = self.r
		    self.vel.y *= -1




class cueBall(Particle):
	def __init__(self, holes=None,*args,**kwargs):
		super().__init__(*args, **kwargs)
		self.c = (255,)*3
		self.vel = Vector(0,0)
		self.add = 0
		self.check = True
		self.oldPos = None
		self.holes = holes

	def update(self, balls, holes):
		self.edges()
		self.pos += self.vel*deltaTime
		self.vel += self.acc*deltaTime
		self.vel *= .995
		self.acc = Vector(0,0)
		self.show()
		self.handleMouse(balls, holes)


	def handleMouse(self, balls, holes):
		global frameRate
		if mouseJustPressed:
			self.P = Vector(*pygame.mouse.get_pos())

		if self.checkCheck(balls):
			v1 = (Vector(*pygame.mouse.get_pos())-self.pos)
			v1 = self.oldPos + (v1-self.oldPos)*.4 if self.oldPos != None else v1
			v = v1.normalized()
			drawLine(self.pos+v*(20+self.add), self.pos+v*(20+self.add)+v*200)
			self.check = True
			self.p = copy.deepcopy(self.pos)
			self.vv = copy.deepcopy(v)
			Trace(self.p, -self.vv, self.r, balls, holes)
			self.oldPos = v1;
		else:
			Trace(self.p, -self.vv, self.r, balls, holes)

		if mousePressed:
			self.add = (Vector(*pygame.mouse.get_pos())-self.P).GetMagnitude()

		elif mouseReleased:
			# frameRate = 12
			self.shoot(-v1*1000*deltaTime)
			# self.vel = (-v1*1000)*deltaTime
			self.add = 0
			self.oldPos = None

	def checkCheck(self, balls):
		out = (self.check or all([(each.vel.GetMagnitude() < .3) for each in balls+[self]]))
		self.check = out
		if self.check:
			for each in balls: each.vel = Vector(0,0)
		return out

	def shoot(self, vel):
		self.vel = vel
		self.check = False 




class Hole(Particle):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def update(self):
		self.show()

	def checkIfIn(self,balls):
		L = len(balls)
		for i in range(L):
			if Hole.isIn(balls[L-i-1].pos, self.pos, balls[L-i-1].r, self.r):
				del balls[L-i-1]
		return balls

	@staticmethod
	def isIn(ballPos, holePos, ballR, holeR):
		return (holePos-ballPos).GetMagnitude() < .4*(holeR+ballR)


class Game():
	def __init__(self):
		self.numBalls = 20+1
		self.i=0
		self.balls = self.getBalls()
		self.holes = self.getHoles()
		self.cueBall = cueBall(holes=self.holes)
		self.vec = bigBrainAlgoParent(self.balls, self.holes,self.cueBall, self.balls[0].r)
		self.s = bigBrainAlgo(self.balls, self.holes, self.balls[0].r)
		print(self.vec, self.s)
		self.pt = self.numBalls
		self.box= Box([Vector(0,0)], h, w, self.pt, particles=self.balls+[self.cueBall])

	def update(self):
		global frameRate
		self.vec = bigBrainAlgoParent(self.balls, self.holes,self.cueBall, self.balls[0].r)
		drawCircle(self.s[0], r=self.balls[0].r, c=(0,0,0))
		try:
			Trace(self.cueBall.pos, self.vec, self.balls[0].r, self.balls, self.holes, depth=2)
		except:
			pass
		if self.i >= 10 and self.cueBall.checkCheck(self.balls):
			self.cueBall.shoot(self.vec*3000)
			# self.s = bigBrainAlgo(self.balls, self.holes, self.balls[0].r)
			# frameRate = 12
			# self.cueBall.vel = self.vec*3000
			self.i = 0
		# self.vec = bigBrainAlgoParent(self.balls, self.holes,self.cueBall, self.balls[0].r)
		for each in self.balls+self.holes: each.update();
		self.cueBall.update(self.balls, self.holes)
		self.box = Box([Vector(0,0)], h, w, self.pt, particles=self.balls+[self.cueBall])
		self.box.CheckCollisions()
		for each in self.holes: 
			self.balls = each.checkIfIn(self.balls);
		self.i = self.i+1 if self.cueBall.checkCheck(self.balls) else self.i

	def getBalls(self):
		return [Particle() for i in range(self.numBalls-1)]

	def cueBall(self):
		return cueBall()

	def getHoles(self):
		return [Hole(pos=Vector(10,10),c=(255,255,255), r=15),
				Hole(pos=Vector(w//2,4),c=(255,255,255), r=15),
				Hole(pos=Vector(w-10,10),c=(255,255,255), r=15),

				Hole(pos=Vector(10,h-10),c=(255,255,255), r=15),
				Hole(pos=Vector(w//2,h-4),c=(255,255,255), r=15),
				Hole(pos=Vector(w-10,h-10),c=(255,255,255), r=15),
				]



def CheckEvent():
	global run, mousePressed, mouseReleased, mouseJustPressed, frameRate
	mouseJustPressed = False
	mouseReleased = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			mousePressed= True
			mouseJustPressed = True

		if event.type == pygame.MOUSEBUTTONUP:
			mousePressed = False
			mouseReleased = True

	keys = pygame.key.get_pressed()
	if keys[pygame.K_d]:
		frameRate += 1
		print(frameRate)
	if keys[pygame.K_a]:
		frameRate -= 1
		print(frameRate)
	return (keys,run)


def CheckCollisions():
	global particles
	for i,p in enumerate(particles[:-1]):
		for another in particles[i+1:]:
			if dist(p,another) < p.r*2:
				reverseVelocities(p,another)

def bigBrainAlgoParent(balls, holes,cueBall, r):
	for ball in balls:
		for hole in holes:
			v = (hole.pos-ball.pos).normalized()
			goesIn, _,_ = Trace(ball.pos, v,r, balls,holes, depth=1,draw=False)
			if goesIn == None:
				continue
			if goesIn:
				pos = ball.pos-v*r*(2)

				# drawCircle(pos, r=r, c=(255, 0, 255))
				# drawLine(cueBall.pos, pos)
				vec = (pos-cueBall.pos).normalized()
				_, p, uhat = Trace(cueBall.pos, vec,r, balls,holes, depth=1,draw=False)
				# drawCircle(p+Vector(-vec.y, vec.x)*2*r, r=r, c=(61,81, 121))
				if (p-uhat*2*r-pos).GetMagnitude() < 1e-7:
					# drawCircle(p-uhat*2*r, r=r, c=(255,255, 0), thick=3)
					# print(pos)
					return vec
	# for hole in holes:
		# v = (hole.pos-ball.pos).normalized()
		# newPos = ball.pos-v*r
		# vperp = Vector(-v.y, v.x)

		# m, b = (vperp.y/vperp.x, newPos.y-(vperp.y/vperp.x)*newPos.x) if vperp.x != 0 else (None,)*2
		# bigBrainAlgo(m, b)

def bigBrainAlgo(balls, holes,r, root=None, L=0):
	global g
	maxB = 0;
	bR = None
	for ball in balls:
		for hole in holes:
			v = (hole.pos-ball.pos).normalized()
			goesIn, _,_ = Trace(ball.pos, v,r, balls,holes, depth=1,draw=False)
			if goesIn == None:
				continue
			if goesIn:
				pos = ball.pos-v*r*(2)
				v90 = Vector(-v.y, v.x)
				_, p, uhat = Trace(pos, v90,r, balls,holes, depth=1,draw=False)
				# if root is not None: 
					# CheckEvent()
					# screen.fill((0,21,21))
					# drawCircle(root, c=(255,255,255), r=r)
					# drawCircle(pos, c=(255,255,255), r=r)
					# try:
					# 	g.update()
					# except:
					# 	pass
					# pygame.display.update()		
				if root is None or (p-uhat*2*r-root).GetMagnitude() < 1e-5:
					R, B = bigBrainAlgo(set(balls)-{ball}, holes,r, pos, L+1)
					if B > maxB:
						maxB = B;
						bR = R
	return (bR, maxB) if bR is not None else (root, L)






do = 0;
fR = 12
g= Game()
def func():
	clock.tick(frameRate)
	CheckEvent()
	screen.fill((0,21,21))
	g.update()
	pygame.display.update()	
while run:
	func()
