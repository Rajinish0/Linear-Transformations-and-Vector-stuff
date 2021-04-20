from Linalg import Vector, Matrix
import math,pygame,time,random,numpy as np,sys
run = True
w,h = 1200,780
scale = 20 ## CONTROLS THE SPACING FOR NUMBERS ON THE NUMBERLINE(yk it's like the scale of zoom), 1 = 1 number per pixel on x and y axes, 2 = 1 number per 2 pixels
clock = pygame.time.Clock()
screen = pygame.display.set_mode((w,h))
maxSpeed = 200
spacing = 50 ## spacing b/w vectors(it's for both on x and y axis)
frameRate = 30
deltaTime = 1/frameRate
vectors = []

def CheckEvent():
	global run
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False
	keys = pygame.key.get_pressed()
	return (keys,run)


class particle:
    def __init__(self,pos,vel=None,acc=None,magnitude=None,dampeningAffect = 1,mass=1,maxTrail=0):
        self.pos = pos
        self.vel = Vector(math.cos(math.radians(random.choice([-180,0]))),math.sin(math.radians(random.choice(range(0,360))))) if vel is None else vel
        self.acc = acc
        self.damp = dampeningAffect
        self.trail = []
        self.maxTrail = 0
        self.speed = 3+scale/10
        self.radius = 3
        self.prevPos = self.pos
    def update(self,screen,deltaTime):
        '''so integral of v is pos, which is xo + vt, so the new pos is, current pos + velocity*howmuch time has passed'''
        '''in our case that would be the time b/w frames, which i could either compute'''
        '''or just be naive and say it's 1/frameRate '''
        self.pos += self.vel *self.speed* deltaTime
        self.vel += self.acc * deltaTime
        self.show();self.edges()
        pygame.draw.line(screen,self.c,(self.prevPos.x,self.prevPos.y),(self.pos.x,self.pos.y),1)
        self.prevPos=self.pos
        if self.maxTrail != 0:
	        if not len(self.trail) >= self.maxTrail:
	            self.trail.append(particle(self.pos))
	        else:
	            self.process()
	        [p.show() for p in self.trail]
        self.acc = Vector(0,0)
    def changeDir(self,direc):
        self.vel = direc
    def applyForce(self,f):
        self.acc += f
    def process(self):
        del self.trail[0]
        self.trail.append(particle(self.pos))
    def setMass(self,mass):
        self.mass = mass
    def CheckCollisions(self):
        if self.pos.x+self.radius > w or self.pos.x-self.radius < 0:
            return True
            #self.velocity.x = -1*self.velocity.x
            #self.velocity.x *= self.damp
        elif self.pos.y-self.radius < 0  or self.pos.y+self.radius > h:
            self.vel.y = -1*self.vel.y
            self.vel.y *= self.damp
    def show(self):
        # pygame.draw.circle(screen,(255,255,255),(int(self.pos.x),int(self.pos.y)),self.radius)
        pass
    def edges(self):
    	if self.pos.x > w:
    		self.pos.x = 1
    		self.prevPos = self.pos
    	if self.pos.y > h:
    		self.pos.y = 1
    		self.prevPos = self.pos
    	if self.pos.x < 0:
    		self.pos.x = w-1
    		self.prevPos = self.pos
    	if self.pos.y< 0:
    		self.pos.x = h-1
    		self.prevPos = self.pos



class DiffRootVector(Vector):
	## ROOT IS A VECTOR
	def __init__(self,root,x,y,angle=0):
		super().__init__(x,y)
		self.root = root
		self.angle = math.degrees(math.atan((self.y)/self.x)) if self.x != 0 else 0
		self.angle = self.angle if angle == 0 else angle
		self.origMag = self.GetMagnitude()
		self.mag = self.clampMagnitude()
		self.sumX = (self.root.x + self.x)
		self.sumY = (self.root.y + self.y)
		self.finPos = Vector(self.sumX,self.sumY)
		self.finPos = self.finPos.rotate(self.root,angle) if angle != 0 else self.finPos;
		self.angle = self.angle + 180 if (self.sumY > self.root.y and self.sumX < self.root.x) or (self.sumY-self.root.y <= 0 and self.root.x > self.sumX) else self.angle
		if self.x == 0:
			if self.sumY > self.root.y:
				self.angle = 90
			else:
				self.angle = -90
		self.arrowVertices = self.GetAVertices()
	def GetAVertices(self):
		dist = 5
		x,y = self.root.x,self.root.y
		x1,y1 = x+self.x,y+self.y
		x2,y2 = x+(self.x-dist),y + self.y-dist
		x3,y3 = x+(self.x-dist),y + self.y+dist
		Vertices = [(Vector(x1,y1),Vector(x2,y2)),(Vector(x1,y1),Vector(x3,y3))]
		for i,(v1,v2) in enumerate(Vertices):
			nv1 = v1.rotate(self.finPos,self.angle)
			nv2 = v2.rotate(self.finPos,self.angle)
			Vertices[i] = (nv1,nv2)
		return Vertices


	def draw(self,screen):
		## MAKE THE COLOR DEPENDENT ON THE VECTOR's length
		## WOULD PROBABLY USE SOME SCALE FUCTION FOR DRAWING THE VECTOR
		#pygame.draw.line(screen,(self.r,0,self.b),(self.root.x,self.root.y),(self.sumX,self.sumY),2)
		pygame.draw.line(screen,(self.r,0,self.b),(self.root.x,self.root.y),(self.finPos.x,self.finPos.y),2)
		for v1,v2 in self.arrowVertices:
			pygame.draw.line(screen,(self.r,0,self.b),(v1.x,v1.y),(v2.x,v2.y),2)
	def clampMagnitude(self):
		maxMag = (w//2)/(scale)
		# maxMag = Vector(func1(w//scale,h//scale),func2(w//scale,h//scale)).GetMagnitude()
		mag = self.GetMagnitude()*(1+((scale-1)/100))
		ratio = mag/maxMag
		ratio = min(1,ratio)
		self.r = 255*ratio
		self.b = 255*(1-ratio)
		new = self.SetMag(np.clip(mag,0,20))
		self.x,self.y = new.x,new.y
		return new

## FUNC1 = y; func2= -x - some resitance term gives simple harmonic motion of a spring
## YOU CAN interpret any position on the 2d plane as the x coordinate being ur deviation from the mean position
## your y coordinate being your velocity at the point so if i increase the resistance term I'll see the
# vectors go down quickly;

##THE OTHER EQUATION IS THE ACCELERATION FOR A PENDULUM; It's from differential equations it's pretty cool

def func1(x,y):
	# return 10
	# return random.randint(-10,10)
	# return y*y*y - 9*y
	# return x*y
	return y
	return x*math.sin(y)
def func2(x,y):
	# return -10
	# return random.randint(-10,10)
	# return x*x*x - 9*x
	# return y*y - x*x
	resistance = .5
	return (-resistance*y)-x
	theta_dot = y
	g = 9.8
	L = 1
	theta = x	
	return -resistance*theta_dot-(9.8/2)*math.sin((x))
	return y*math.cos(x)

def go():
	global vectors,spcaing
	for x in range(0,w,spacing):
		for y in range(0,h,spacing):
			print(x,w,scale)
			reX,reY = ((x)-(w//2))/scale,(((y)-(h//2)))/scale
			print(reX,reY)
			v1 = func1(reX,reY)
			v2 = func2(reX,reY)
			newV = DiffRootVector(Vector(x,y),v1,v2)
			print(v1,v2)
			vectors.append(newV)
			#time.sleep(1)


def go1():
	global vectors,spcaing
	for x in range(0,w,spacing):
		for y in range(0,h,spacing):
			clock.tick(1000)
			screen.fill((0,0,0))
			reX,reY = ((x)-(w//2))/scale,(((y)-(h//2)))/scale
			v1 = func1(reX,reY)
			v2 = func2(reX,reY)
			newV = DiffRootVector(Vector(x,y),v1,v2)
			vectors.append(newV)
			[v.draw() for v in vectors]
			pygame.display.update()
			CheckEvent()

def flow(boid,colored):
	global spacing,vectors
	x,y = boid.pos.x,boid.pos.y
	x,y = int(x//spacing), int(y//spacing)
	VectorsOnY = (h//spacing)+1 if h%spacing != 0 else h//spacing
	ind = (x*VectorsOnY)+y
	try:
		force = vectors[ind]
		# pygame.draw.circle(screen,(255,255,255),(force.root.x,force.root.y),3)
		acc = Vector(force.x,force.y)
		acc = acc.SetMag(force.origMag*2)
		boid.applyForce(acc)
		boid.c = (force.r,0,force.b) if colored else (51,51,51) ## set the color to the vector's color or jus gray		
	except:
		boid.c = (51,51,51)


if __name__ == '__main__':
	go()
	animation = 0
	colored = False
	ps = [particle(Vector(random.randint(0,w),random.randint(0,h)),Vector(0,0),Vector(0,0),maxTrail =0) 
			for i in range(500)]
	while run:
		for p in ps:
			flow(p,colored);p.update(screen,.2);p.update(screen,.2);p.vel = Vector(0,0)
		if animation:
			go1()
			animation= False
		[v.draw(screen) for v in vectors]
		pygame.display.update()
		keys,run = CheckEvent()
