import pygame, sys
from Linalg import *
import math,time,random,os
import matplotlib.pyplot as plt
from functools import reduce
import svg.path
from xml.dom import minidom
sys.setrecursionlimit(5000)


sin = math.sin
cos = math.cos
rad = math.radians
pi = math.pi
w,h = 1000,800
CX, CY = 0,0
C = 0

def drawCircle(v,c=(255,255,255), r=2, thick=0):
	pygame.draw.circle(screen, c, (((v.x-CX-w//2)*C+v.x,(v.y-CY-h//2)*C+v.y) if type(v) == Vector else ((v.real-CX-w//2)*C+v.real, (v.imag-CY-h//2)*C+v.imag)), r*(C+1),thick)

def drawLine(v1,v2,c=(255,255,255),thick=2):
	pygame.draw.line(screen, c, (((v1.x-CX-w//2)*C+v1.x,(v1.y-CY-h//2)*C+v1.y) if type(v2) == Vector else ((v1.real-CX-w//2)*C+v1.real, (v1.imag-CY-h//2)*C+v1.imag)),
								(((v2.x-CX-w//2)*C+v2.x,(v2.y-CY-h//2)*C+v2.y) if type(v2) == Vector else ((v2.real-CX-w//2)*C+v2.real, (v2.imag-CY-h//2)*C+v2.imag)), thick)




def clip(v, l, u):
	return max(min(v, u), l)

def loadSVG(path, scale = .8, numPoints=2000):
	print('loading')
	doc = minidom.parse(path)
	path= doc.getElementsByTagName('path')[0].getAttribute('d')
	p = svg.path.parse_path(path)
	points = [Vector(each.real, each.imag) for each in [p.point(pos) for pos in np.linspace(0,1,numPoints)]]
	A = reduce(lambda x, y : x+y, points)/len(points)
	points = [scale*(each-A)+Vector(w//2,h//2) for each in points]
	print('done')
	return points


def getFunc(n):
	def expi(t, n=n):
		return np.cos(2*pi*n*t) + np.sin(2*pi*n*t)*complex(0, 1)
	return expi

class FourierSeries():
	def __init__(self):
		self.done = False
		self.ps = []
		pass


	def do(self, points, numV=5,needsFix=False):
		self.points = self.fix(points) if needsFix else points
		self.points = np.array([complex(v.x, v.y) for v in self.points])
		self.tP=len(self.points)
		self.numV = numV		
		self.funcs, self.coeffs = self.getCoeffs()
		self.t = 0
		self.i = 0
		self.done = True
		self.colors = [(random.randint(0,255),random.randint(0, 255),181) for i in range(numV)]


	def fix(self, points):
		return [each-Vector(w//2, h//2) for each in points]

	def getCoeffs(self):
		coeffs = []
		funcs = []
		timeSteps=np.linspace(0, 1, len(self.points))

		coeffs.append((self.points/self.tP).sum())
		funcs.append(getFunc(0))

		for i in range((self.numV-1)//2):
			funcs.append(getFunc(i+1))


			coeffs.append((self.points*funcs[-1](timeSteps)/self.tP).sum())

			funcs.append(getFunc(-i-1))

			coeffs.append((self.points*funcs[-1](timeSteps)/self.tP).sum())
		return funcs, coeffs

	def update(self):
		if self.done:
			self.draw()

	def draw(self):
		global CX, CY
		vs, p = self.predict(self.t)
		point = Vector(p.real+w//2, p.imag+h//2)
		CX, CY = point.x-w//2, point.y-h//2
		# drawCircle(point, r=2)
		self.t = (self.t+(1/(2*self.tP)))%(1)
		self.ps.append(point)
		[drawLine(self.ps[i], self.ps[i+1], c=(181,181,21), thick=3) for i in range(len(self.ps)-1)]
		self.drawvs(vs)
		if len(self.ps) >= 2*self.tP or self.i:
			self.ps = self.ps[1:]
			self.i = 1

	def drawvs(self, vs):
		S = lambda x, y : x+y
		F = [complex(0,0)] + [reduce(S, vs[:i]) for i in range(1, len(vs))]
		T = complex(w//2, h//2)
		[(drawLine(F[i]+T, F[i]+vs[i]+T, c=self.colors[i]), 
		  drawCircle(F[i]+vs[i]/2+T,c=self.colors[i], r=pow(vs[i].real**2 + vs[i].imag**2, .5)/2, thick=1)) for i in range(len(F))]



	def predict(self,t):
		vs = [self.coeffs[i]*self.funcs[i](t) for i in range(len(self.coeffs))]
		return vs, sum(vs)


def getCircle(r=50):
	p = []
	i = 0
	while i < 360:
		p.append(Vector(cos(rad(i)), 
						sin(rad(i)))*r +Vector(w//2, h//2))
		i += .01
	return p



# points = getCircle()
# points = []
# F = FourierSeries(points)
# timeSteps = np.linspace(0, 1, len(points))
# print((F.points*getFunc(0)(timeSteps)/len(points)).sum())
# print(reduce(lambda x, y: x+y, points))


# for i in range(100):
	# print(F.predict(i/len(points))

points = getCircle()

def removeNN(L, num=10):
	i = 0
	while i < len(L):
		Q = sorted(L, key=lambda x: (L[i]-x).GetMagnitude())
		[L.remove(each) for each in Q[1:num+1]]
		i += 1
	return L



class Game():
	def __init__(self):
		# self.points = getCircle()
		# self.points = [2*(Vector(*[float(e.strip()) for e in each.strip('\n')[1:-1].split(',')])-Vector(w//2, h//2)) + Vector(w//2, h//2) for each in open('batmanBestPath.txt').readlines()]
		# self.points = removeNN(self.points, 4)
    '''
    CHANGE PATH.
    '''
		self.points = loadSVG('d:\\Raj.svg')#[1482:] 
		# self.points = []
		self.prevp = None
		self.fouier = FourierSeries()

	def update(self,keys):
		self.handleKeys(keys)
		self.handleMouse()
		[drawCircle(each) for each in self.points]
		# [drawLine(self.points[i], self.points[i+1], c=(51,51,51), thick=3) for i in range(len(self.points)-1)]
		self.fouier.update()

	def handleKeys(self,keys):
		global C
		if keys[pygame.K_s]:
			self.fouier.do(self.points, 300,needsFix=True)
			time.sleep(.5)
			del self.points
			self.points = []

		if keys[pygame.K_k]:
			C -= 1
			C = clip(C, 0, 5000)
			print(C)

		if keys[pygame.K_l]:
			C += 1
			C = clip(C, 0, 5000)
			print(C)

		if keys[pygame.K_c]:
			self.fouier.colors[:-1] = [(21,21,21)]*self.fouier.numV


	def handleMouse(self):
		curp = Vector(*pygame.mouse.get_pos())
		if mouseJustPressed:
			self.prevp = curp
			self.points.append(curp)

		if mousePressed and dist(curp, self.prevp) > 1:
			print('yes')
			self.points.append(curp)
			self.prevp = curp

def dist(v1, v2):
	return pow((v2.x-v1.x)**2 + (v2.y-v1.y)**2, .5)

def CheckEvent():
	global run, mousePressed, mouseReleased, mouseJustPressed
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
	return (keys,run)

def drill(funcs=[]):
	screen.fill((0,0,0))
	keys,_ = CheckEvent()
	g.update(keys)
	for func, args in funcs:
		func(*args)
	pygame.display.update()

def dist(v1, v2):
	return pow((v2.x-v1.x)**2 + (v2.y-v1.y)**2, .5)


# print(points[:5])

if __name__ == '__main__':
	run = True
	w,h = 1000,800
	screen = pygame.display.set_mode((w,h))
	imgs = []
	i = 0
	path = 'd:\\pygameImages1'
	if not os.path.exists(path):
		os.mkdir(path)
	# clock = pygame.time.Clock()
	mousePressed = False
	mouseJustPressed = False
	mouseReleased = False
	dont= False
	dtheta = .3

	g=  Game()
	while run:
		drill();
		# imd = pygame.surfarray.array3d(screen)
		# imd = imd.swapaxes(0,1)
		# imgs.append(screen.copy())
		# if i % 100:
			# [pygame.image.save(s, path+f'\\img{str(i).zfill(6)}.jpg') for s in imgs]
			# [np.save(path+f'img{str(i).zfill(6)}.npy', imd) for imd in imgs]
			# imgs = []
		# sao
		# imgs.append(screen.copy())
		# i+=1
	# L = len(imgs)
	# numDigits = np.floor(math.log(L)/math.log(10)) + 1
	# for i, each in imgs:
		# pygame.image.save(each, path+f'\\img{i}.jpg')


