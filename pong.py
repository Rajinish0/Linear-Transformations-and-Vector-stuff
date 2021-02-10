import pygame,copy,math,random
from pygame.locals import *
from Linalg import Vector,Matrix
pygame.init()
clock = pygame.time.Clock()
frameRate = 60
deltaTime = 1/frameRate
w,h = 700,480
screen = pygame.display.set_mode((w,h))
gravity = Vector(0,9.8)
postImpactVelocity = 450

class particle:
    def __init__(self,pos,vel=None,acc=None,magnitude=None,dampeningAffect = 1,mass=1):
        self.pos = pos
        self.velocity = Vector(math.cos(math.radians(random.choice([-180,0]))),math.sin(math.radians(random.choice(range(0,360))))) if not vel is None else None
        self.acceleration = acc
        self.damp = dampeningAffect
        self.trail = []
        self.maxTrail = 3
        self.speed = 200
        self.mass=mass
        self.radius = 4
    def update(self,screen):
        '''so integral of v is pos, which is xo + vt, so the new pos is, current pos + velocity*howmuch time has passed'''
        '''in our case that would be the time b/w frames, which i could either compute'''
        '''or just be naive and say it's 1/frameRate '''
        self.pos += self.velocity*self.speed * deltaTime
        self.velocity += self.acceleration * deltaTime
        self.show()
        if not len(self.trail) >= self.maxTrail:
            self.trail.append(particle(self.pos))
        else:
            self.process()
        [p.show() for p in self.trail]
        self.acc = 0
    def changeDir(self,direc):
        self.velocity = direc
    def applyForce(self,f):
        self.acc += self.f
    def process(self):
        del self.trail[0]
        self.trail.append(particle(self.pos))
    def setMass(self,mass):
        self.mass = mass
    def CheckCollisions(self):
        if self.pos.x+self.radius > w or self.pos.x-self.radius < 0:
            return not (leftPlank.CheckCollision(self) or rightPlank.CheckCollision(self,False))
            #self.velocity.x = -1*self.velocity.x
            #self.velocity.x *= self.damp
        elif self.pos.y-self.radius < 0  or self.pos.y+self.radius > h:
            self.velocity.y = -1*self.velocity.y
            self.velocity.y *= self.damp
    def show(self):
        pygame.draw.circle(screen,(255,255,255),(int(self.pos.x),int(self.pos.y)),self.radius)
        
            
class Plank:
    def __init__(self,coords,right=False):
        self.pos = coords
        self.w= 10
        self.h = 100
        self.speed = 12
        self.right =right
        self.rect = Rect(self.pos.x,self.pos.y,self.w,self.h) if not right else Rect(self.pos.x-self.w//2,self.pos.y,self.w,self.h)
        
        
    
    def update(self,screen):
        pygame.draw.rect(screen,(255,255,255),self.rect)
        
        
    
    def chdir(self,direc):
        if (direc is -1 and not self.pos.y < 0)  or (direc is 1 and not self.pos.y+self.h >h):
            self.pos.y += direc*self.speed
            self.rect =Rect(self.pos.x,self.pos.y,self.w,self.h) if not self.right else Rect(self.pos.x-self.w//2,self.pos.y,self.w,self.h)
            
    @staticmethod
    def constrain(cur,total,maximum):
        print(cur/total)
        return ((cur*abs(maximum)*2)/total)-maximum

    
    def DoTheStuff(self,ball,left):
        center=Vector(0,0)
        ball.speed = postImpactVelocity
        ball.velocity.x *= -1
        velx = ball.velocity.x
        magnitude = ball.velocity.GetMagnitude()
        bottom = self.pos.y + self.h
        distFromBottom = bottom - h
        ballDist = ball.pos.y - h    
        cur = abs(ballDist-distFromBottom)
        sign = -1 if left else 1
        rotation=Plank.constrain(cur,sign*self.h,sign*75)
        ball.velocity.rotate(center,rotation)
        ball.velocity = ball.velocity.normalized()*magnitude
        ball.velocity.x=velx  
    
    def CheckCollision(self,ball,left=True,threshold=15):
        global w,h
        collided = False
        
        if not left:
            if ball.pos.x >= self.pos.x-self.w and self.pos.y<ball.pos.y<self.pos.y+self.h and not ball.velocity.x/abs(ball.velocity.x) == -1:
            	self.DoTheStuff(ball,left);
            	return True

        else:
            if ball.pos.x <= self.pos.x+self.w and self.pos.y<ball.pos.y<self.pos.y+self.h and not ball.velocity.x/abs(ball.velocity.x) == 1:
            	self.DoTheStuff(ball,left);
            	return True
        return False

        
        
run = True
initPos = Vector(w//2,h//2)
initVel = Vector(300,-80)
initacc = Vector(0,0)
myParticle = particle(initPos, initVel, initacc,initVel.GetMagnitude())
leftPlank = Plank(Vector(0,(h//2)-60//2))
rightPlank = Plank(Vector(w-4,(h//2)-60//2),True)
while run:
    clock.tick(frameRate)
    screen.fill((100,0,100))
    leftPlank.update(screen)
    rightPlank.update(screen)
    leftPlank.CheckCollision(myParticle)
    rightPlank.CheckCollision(myParticle,False)
    roundOver= myParticle.CheckCollisions()
    if roundOver:
        myParticle = particle(initPos,initVel,initacc,initVel.GetMagnitude())
    myParticle.update(screen)
    pygame.display.update()
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
    if keys[pygame.K_UP]:
        rightPlank.chdir(-1)
    elif keys[pygame.K_DOWN]:
        rightPlank.chdir(1)

    if keys[pygame.K_w]:
        leftPlank.chdir(-1)
    elif keys[pygame.K_s]:
        leftPlank.chdir(1)     