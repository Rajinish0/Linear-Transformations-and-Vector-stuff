import pygame,random,math,numpy as np,copy
from Linalg import Vector,Matrix
pygame.init()
w, h = 900,680
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
run = True
frameRate = 60
deltaTime = 1/frameRate

class Boid:
	def __init__(self):
		self.pos = Vector(random.randint(0,w),random.randint(0,h))
		self.vel = Vector(math.cos(random.uniform(0,2*3.14)),math.sin(random.uniform(0,2*3.14)))
		self.acc = Vector(0,0)
		self.r = 10
		self.angle = 0
		self.maxSpeed = 5
		self.vertices = self.GetVertices()
	def GetVertices(self):
		r = self.r
		topVertex = Vector(self.pos.x+r,self.pos.y)
		bottomLeft = Vector(self.pos.x-r,self.pos.y-r)
		bottomRight = Vector(self.pos.x-r,self.pos.y+r)
		return [topVertex,bottomLeft,bottomRight]
	def ChaseTarget(self,pos):
		pos = Vector(pos[0],pos[1])
		direction = pos-self.pos
		#self.vel = direction
		self.applyForce(direction-self.vel)
	def applyForce(self,f):
		self.acc += f
	def update(self,screen,deltaTime):
		self.pos += self.vel*deltaTime
		self.vel += self.acc*deltaTime
		self.vertices = self.GetVertices()
		pygame.draw.line(screen,(0,255,0),(self.pos.x,self.pos.y),(-self.vel.x+self.pos.x,-self.vel.y+self.pos.y),2)
		norm = (self.vel.normalized())
		## THIS IS BASICALLY ARCTAN(x/y) but um idk precision errors were giving me wrong answers
		## NP works..
		angle = np.angle(np.array([complex(norm.x,norm.y)]),deg=True)[0]
		#print(angle,norm)
		self.acc = Vector(0,0)
		self.rotate(angle)
	def SetVel(self,vel):
		self.vel = vel
		return self
	def SetAcc(self,acc):
		self.acc = acc
		return self
	def draw(self,screen):
		vert=self.vertices
		for i in range(1,len(self.vertices)):
			pygame.draw.line(screen,(255,255,255),(vert[i-1].x,vert[i-1].y),(vert[i].x,vert[i].y),2)
		pygame.draw.line(screen,(255,255,255),(vert[0].x,vert[0].y),(vert[-1].x,vert[-1].y),2)
	def rotate(self,angle):
		self.angle = angle
		for each in self.vertices:
			each.rotate(self.pos,angle)


class NewBoid(Boid):
	def __init__(self):
		super().__init__()
		self.maxSpeed = 180
	def AvgVelToOthers(self,boids):
		avgVel = Vector(0,0)
		avgPos = Vector(0,0)
		velThreshold =10
		posThreshold = 10
		total = 0
		totalPos = 0
		for each in boids:
			if each != self and dist(self,each) < velThreshold**2:
				avgVel += each.vel
				total += 1
			if each != self and dist(self,each) < posThreshold**2:
				avgPos += each.pos
				totalPos +=1
			if each != self and dist(self,each) < (self.r*2+15)**2:
				# self.applyForce(each.vel)
				ElasticCollision(self,each)
		if not total is 0:
			avgVel = avgVel / total
			self.applyForce(avgVel - self.vel)
		if not totalPos is 0:
			avgPos = avgPos/totalPos
			self.applyForce(avgPos-self.pos)
	def FixPos(self):
		if self.pos.x+self.r > w:
		    self.pos.x = 15
		if self.pos.x-self.r < 0:
		    self.pos.x = w-15
		if self.pos.y+self.r > h:
		    self.pos.y = 15
		if self.pos.y-self.r < 0:
		    self.pos.y =h-15
	def update(self,boids):
		self.FixPos()
		self.AvgVelToOthers(boids)
		# print(self.vel)
		self.pos += self.vel.normalized()*self.maxSpeed*deltaTime
		#print(self.vel,self.acc)
		self.vel += self.acc*deltaTime
		self.vertices = self.GetVertices()
		# pygame.draw.line(screen,(0,255,0),(self.pos.x,self.pos.y),(-self.vel.x+self.pos.x,-self.vel.y+self.pos.y),2)
		norm = (self.vel.normalized())
		angle = np.angle(np.array([complex(norm.x,norm.y)]),deg=True)[0]
		# print(angle,norm)
		self.acc = Vector(0,0)
		self.rotate(angle)

def dist(v1,v2):
    return (pow(v2.pos.x-v1.pos.x,2)+pow(v2.pos.y-v1.pos.y,2))

### ELASTIC COLLISION FOR EQUAL MASS OBJECTS 
def ElasticCollision(p1,p2):
    first = copy.deepcopy(p1.vel)
    second = copy.deepcopy(p2.vel)
    disgust = 2
    p1.applyForce(disgust*second)
    p2.applyForce(disgust*first)
    #p1.vel = second
    #p2.vel = first


if __name__ == '__main__':
	boids = [NewBoid() for i in range(34)]
	print(Vector(random.randint(0,w),random.randint(0,h)).normalized())
	ang = 0
	while run:
		clock.tick(frameRate)
		screen.fill((0,0,0))
		[(boid.update(boids),boid.draw(screen)) for boid in boids]
		# [(	boid.ChaseTarget(pygame.mouse.get_pos()),
		# boid.update(screen),
		# boid.draw(screen)) for boid in boids]
		#boid.ChaseTarget(pygame.mouse.get_pos())
		#boid.update()
		#boid.draw()
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				run = False