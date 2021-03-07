#from exp import Boid
import numpy as np
from Linalg import Vector,Matrix
import pygame,random,math,time,copy
from vf import DiffRootVector
from NEAT import *
from functools import reduce
from sklearn.preprocessing import StandardScaler
run = True
w,h = 1200,780
clock = pygame.time.Clock()
screen = pygame.display.set_mode((w,h))
maxSpeed = 200
frameRate = 30
angleTurn = 10
FOV = 360//2
deltaTime = 1/frameRate
cos = math.cos
sin = math.sin
rad = math.radians


imgPath = 'myCar.png'

class Car:
	def __init__(self):
		self.pos = (Vector(w//2+250+75,h//2))
		self.vel = Vector(0,0)
		self.acc = Vector(0,0)
		self.car = False
		#self.img = pygame.image.load(imgPath)
		#self.img = self.img.convert_alpha()
		#self.img = pygame.transform.scale(self.img,(52,52))
		#self.OrigImg = copy.copy(self.img)
		self.r = 10
		self.shouldDie = False
		self.lastCrossed = 0
		self.angle = 0
		self.maxSpeed = 5
		self.dampening = .99
		self.prev = 0
		self.vertices = self.GetVertices()
	#	self.headingVector = self.vertices[0]-self.pos
		self.score = 0
		self.down = False
		self.normalVector = self.GetNormalVector()

	## TRIANGLE
	def GetVertices(self,pos=None,shape='SQUARE'):
		if shape == 'TRIANGLE':
				r = self.r
				pos = self.pos if pos is None else pos
				topVertex = Vector(self.pos.x+r,self.pos.y)
				bottomLeft = Vector(self.pos.x-r,self.pos.y-r)
				bottomRight = Vector(self.pos.x-r,self.pos.y+r)
				return [topVertex,bottomLeft,bottomRight]
		elif shape == 'SQUARE':
				r = self.r
				pos = self.pos if pos is None else pos
				topLeft = Vector(self.pos.x-r,self.pos.y+r)
				topRight = Vector(self.pos.x+r,self.pos.y+r)
				bottomLeft = Vector(self.pos.x-r,self.pos.y-r)
				bottomRight = Vector(self.pos.x+r,self.pos.y-r)
				return [topLeft,topRight,bottomRight,bottomLeft]
		else:
			raise Exception(shape + ' is invalid, puta.');



	def adjustVelocity(self):
		v1 = (self.normalVector-self.pos).normalized()
		v2 = (self.vel).normalized()
		try:
			angBw = math.acos(v1.dot(v2))*180/math.pi
			angBw = 0 if abs(angBw)<1 else angBw
		except:
			angBw = 180 if self.down else 0 
		ang = self.angle + 180 if angBw != 0 else self.angle
		ve= Vector(math.cos(0),math.sin(0))*self.vel.GetMagnitude()
		ve.rotate(Vector(0,0),ang)
		self.vel =ve
	def ChaseTarget(self,pos):
		pos = Vector(pos[0],pos[1])
		direction = pos-self.pos
		#self.vel = direction
		self.applyForce(direction-self.vel)
	def applyForce(self,f):
		self.acc += f
	def updateVertices(self):
		for each in self.vertices:
			each += self.vel*deltaTime;
	def GetNormalVector(self):
		dist = 20;
		v = DiffRootVector(self.pos,dist,0,angle=self.angle);
		return v.finPos;
	def update(self,screen):
		if not self.angle == self.prev:
			self.adjustVelocity()
		self.pos += self.vel*deltaTime
		self.vel += self.acc*deltaTime
		self.normalVector = self.GetNormalVector()
		self.vertices = self.GetVertices(self.pos)
		self.rotate(self.angle)
		self.acc = Vector(0,0)
		self.vel *= self.dampening
		self.ConstructEndPoints()
		self.CheckIfCrossedLandMarks()
		self.prev = self.angle
	def UpdateAngle(self,angle):
		self.angle += angle
		if self.angle > 360:
			self.angle = self.angle- 360
		elif self.angle < 0:
			self.angle = 360-self.angle
	def SetVel(self,vel):
		self.vel = vel
		return self
	def SetAcc(self,acc):
		self.acc = acc
		return self
	def draw(self,screen):
		global img
		if not self.car:
			vert=self.vertices
			done = False	
			for i in range(1,len(self.vertices)):
				c = (255,255,255) if not done else (255,0,0)
				pygame.draw.line(screen,c,(vert[i-1].x,vert[i-1].y),(vert[i].x,vert[i].y),2)
				done = not done
			pygame.draw.line(screen,(255,255,255),(vert[0].x,vert[0].y),(vert[-1].x,vert[-1].y),2)
		else:
			screen.blit(self.img,(self.pos.x,self.pos.y))
	def rotate(self,angle):
		global maxSpeed
		if not self.car:
			for i,each in enumerate(self.vertices):
				self.vertices[i] = each.rotate(self.pos,self.angle)
		else:
			self.img = pygame.transform.rotate(self.OrigImg,-angle)
		return self

	def ConstructEndPoints(self):
		l = []
		for i in range(len(self.vertices)-1):
			l.append((self.vertices[i],self.vertices[i+1]))
		l.append((self.vertices[0],self.vertices[-1]))
		self.segments = l

	def CheckForCollision(self,bound):
		for each in self.segments:
			x1,y1 = each[0]
			x2,y2 = each[1]

			pos =CollisionPoint((x1,y1,x2,y2),(bound.x1,bound.y1,bound.x2,bound.y2))
			if pos is None :
				continue
			x,y = pos
			if (min(x1,x2)<=x<=max(x1,x2) and min(y1,y2)<=y<=max(y1,y2)) and (min(bound.x1,bound.x2)<=x<=max(bound.x1,bound.x2) and min(bound.y1,bound.y2)<=y<=max(bound.y1,bound.y2)):
				pygame.draw.circle(screen, (255,255,255),(int(x),int(y)),5)
				return True
			if self.shouldDie:
				return True
		return False

	def hasCollided(self,bounds):
		for bound in bounds:
			if self.CheckForCollision(bound):
				return True
		return False


	def CheckIfCrossedLandMarks(self):
		self.lastCrossed += 1
		for each in self.landMarks:
			if (self.pos - each).GetMagnitude() < 80:
				self.landMarks.remove(each);
				self.score  = self.score +1 if not self.down else self.score
				self.lastCrossed = 0
		if self.landMarks == []:
			self.landMarks = copy.deepcopy(self.origlandMarks)

		if self.lastCrossed > 120:
			self.shouldDie = True

def CheckEvent():
	global run
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
	keys = pygame.key.get_pressed()
	return keys


def DrawCircularPath(r,pos,shapeSides = 9,animate=True,putLandMarks=False):
	global boundries,landMarks,numlandMarks
	i = 0
	## TO MAKE A NONAGON I HAVE TO MAKE AN INCREAMENT OF 40, because yk all the opposite side are 40 degrees
	## I CAN ACTUALLY MAKE ANY REGULAR POLYGON, all I have to do is increments = 360/# of sides
	## SO YEA A CIRCLE IS ACTUALLY A POLYGON WITH INFINITE SIDES
	increments = 360/shapeSides
	x1,y1 = pos.x+r,pos.y
	while i < 360:
		i += increments
		noise = 0
		x2 = pos.x+(r+noise)*math.cos(math.radians(-i))
		y2 = pos.y+(r+noise)*math.sin(math.radians(-i))
		boundries.append(Boundry(Vector(x1,y1),Vector(x2,y2)))	
		if animate:
			pygame.draw.line(screen,(255,255,255),(x1,y1),(x2,y2),2)
			clock.tick(100)
			pygame.display.update()
			CheckEvent()
		if putLandMarks and int(i % ((increments)/numlandMarks)) == 0:
			landMarks.append(Vector(pos.x+(250 + (r-250) / 2)*math.cos(math.radians(-i)),(pos.y+(250 +(r-250)/2)*math.sin(math.radians(-i)))))
		x1,y1 = x2,y2

class Boundry():
	def __init__(self,initVec,endVec):
		self.initVec = initVec;
		self.endVec = endVec;
		self.x1,self.y1,self.x2,self.y2 = self.initVec.elems+self.endVec.elems
	def draw(self):
		pygame.draw.line(screen,(255,255,255),(self.x1,self.y1),(self.x2,self.y2),2)

def CollisionPoint(line1,line2):
	x11,y11,x21,y21 = line1
	x12,y12,x22,y22 = line2
	m1 = (y21 - y11)/(x21-x11) if x21 - x11 != 0 else float('inf')
	m2 = (y22 - y12)/(x22-x12) if x22 - x12 != 0 else float('inf')
	b1 = y11 - (m1 * x11)
	b2 = y12 - (m2*x12)
	denom = m1 - m2
	if denom == 0:
		return None
	x = (b2 - b1)/denom
	y = (m1*b2-m2*b1)/denom
	return (x,y)

class Ray():
    def __init__(self,coords = None):
        global w,h
        if coords is None:
            self.x1 = w//2
            self.y1 = h//2
            self.x2 = self.x1 + 20
            self.y2 = self.y1
        else:
            self.x1,self.x2,self.y1,self.y2 = coords
        self.visibilityThreshold = 100000
        self.recordDist = 1000000000
        self.bestCoords = (self.x2,self.y2)
    def show(self,pos=None):
        if pos == None:
            pygame.draw.line(screen, (255,0,0,100),(self.x1,self.y1),(self.x2,self.y2))
        else:
            pygame.draw.line(screen, (255,0,0,100),(self.x1,self.y1),pos)
    def trace(self,bound):
        global screen
        pos = CollisionPoint((self.x1,self.y1,self.x2,self.y2),(bound.x1,bound.y1,bound.x2,bound.y2))
        if pos is None:
        	return
        (x,y) = pos
        #if bound.x2 - bound.x1 != 0 and bound.y2-bound.y1 != 0:
  #          x0 = (x-bound.x1)/(bound.x2 - bound.x1)
    #        x1 = (y-bound.y1)/(bound.y2 - bound.y1)
         #       return None
        if x > self.x1 and (90 < self.angle <270):
            return None
        if x < self.x1 and (270 < self.angle or self.angle<90):
            return None
        if y > self.y1 and (180 < self.angle <360):
            return None
        if y < self.y1 and (180 > self.angle >0):
            return None
        if (min(bound.x1,bound.x2)<=x<=max(bound.x1,bound.x2) and min(bound.y1,bound.y2)<=y<=max(bound.y1,bound.y2)):
            return (x,y)
    def getBestCoords(self,bound):
    	coords = self.trace(bound)
    	if coords is not None:
    		x,y = coords
    		d= dist(coords,(self.x1,self.y1)) 
    		if d< self.visibilityThreshold and d < self.recordDist:
    			self.recordDist = d
    			self.bestCoords =(x,y)
    def drawLine(self):
    	pygame.draw.line(screen, (255,0,0),(self.x1,self.y1),self.bestCoords,2)


def dist(p1,p2):
	x1,y1,x2,y2 = [*p1,*p2]
	return pow(x2-x1,2)+pow(y2-y1,2)

def CreateRays(pos=None,rot = 0):
    global w, h,FOV
    rays = []
    if pos is None:
        x1 = w // 2 
        y1 = h//2
    else:
        x1,y1 = pos
    for i in range(-FOV,FOV,INCREAMENT):
        x2 = x1+(20*math.cos(math.radians(i+rot))) 
        y2 = y1 +(20*math.sin(math.radians(i+rot)))
        ray = Ray((x1,x2,y1,y2))
        if i + rot > 360:
            ray.angle = ((i+rot)-360)
        else:
            ray.angle = (i+rot) if (i+rot) > 0 else abs(360+(i+rot))
        if ray.angle < 0 or ray.angle > 360:
            print(ray.angle,i, rot)
        assert 0<= ray.angle <= 360
        rays.append(ray)
    return rays


def CreateRaysForBoid(boid):
    sign = -1 if boid.down else 1
    rays = CreateRays((boid.pos.x+boid.r*cos(rad(boid.angle)),boid.pos.y+boid.r*sin(rad(boid.angle))),boid.angle);
    return rays

def setLandMarks(pop):
	global landMarks
	for each in pop:
		each.phenotype.landMarks = copy.deepcopy(landMarks)
		each.phenotype.origlandMarks = copy.deepcopy(landMarks)
# boid = Car()
# rays = CreateRaysForBoid(boid)
boundries =[]
animate= True
landMarks = []
numlandMarks = 15
DrawCircularPath(400,Vector(w//2,h//2),animate=animate,putLandMarks=True)
DrawCircularPath(250,Vector(w//2,h//2),animate=animate)
INCREAMENT = 30
neat = setup(Car,360//INCREAMENT,4,max_pop = 25)

# boid.landMarks = landMarks
# boid.origlandMarks = copy.deepcopy(landMarks)

pop = copy.copy(neat.population)
setLandMarks(pop)
# boid = Car()
# dna = torch.load('D:\\model_.pt')
# boid.landMarks = landMarks
# boid.origlandMarks = copy.deepcopy(landMarks)
while run:	
	# clock.tick(frameRate)
	clock.tick(1000)
	screen.fill((0,0,0))
	[boundry.draw() for boundry in boundries]
	keys = CheckEvent()
	for dna in pop:
		boid = dna.phenotype
		boid.update(screen)
		boid.draw(screen)
		rays = CreateRaysForBoid(boid);
		# [ray.show() for ray in rays]
		[ray.getBestCoords(bound) for ray in rays for bound in boundries]
		[pygame.draw.circle(screen,(255,0,255),(int(pos.x),int(pos.y)), 5) for pos in boid.landMarks]
		features = torch.from_numpy(StandardScaler().fit_transform(np.array([ray.recordDist for ray in rays]).reshape(-1,1))).reshape(1,-1).float()
		pred = torch.argmax(dna.network(features)).item()
		# print(pred)
		# [ray.drawLine() for ray in rays]
		if boid.hasCollided(boundries):
			dna.score = boid.score
			pop.remove(dna)

		dir = Vector(0,0)
		pygame.display.update()
		# if keys[pygame.K_r]:
			# boid.pos = Vector(w//2,h//2)

		# if keys[pygame.K_w]:
		# print(pred)
		if pred == 0:
			dir += maxSpeed*Vector.up()
			boid.down = False
		# if keys[pygame.K_s]:
		elif pred == 1:
			dir += maxSpeed*Vector.down()
			boid.down = True


		if pred == 2:
		# if keys[pygame.K_a]:
		 	boid.UpdateAngle(-angleTurn)
		# if keys[pygame.K_d]:
		elif pred == 3:
		 	boid.UpdateAngle(angleTurn)
		ang = (boid.normalVector-boid.pos).heading()
		dir.rotate(Vector(0,0),ang+90)
		boid.applyForce(dir);

	if pop == []:
		torch.save(neat.population[neat.fitness.index(max(neat.fitness))].network, 'D:\\model_.pt')
		neat.population = neat.reproduce()
		pop = copy.copy(neat.population)
		setLandMarks(pop)

