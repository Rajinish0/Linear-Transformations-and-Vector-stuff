import pygame,random,math,copy
pygame.init()
w,h = 600,480
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
run = True
currentLetter = 65
random.seed(42)


class Point():
    def __init__(self):
        global currentLetter
        self.x = random.randint(0,w)
        self.y = random.randint(20,h)
        self.radius = 4
        self.color = (255,255,255)
        self.connectsTo = {}
        font = pygame.font.Font('freesansbold.ttf', 15) 
        self.text = font.render(chr(currentLetter), True, (0,255,0)) 
        self.textRect = self.text.get_rect()  
        self.textRect.center = (self.x, self.y-(self.radius+10))
        self.letter = chr(currentLetter)
        currentLetter += 1
        self.update()
    def update(self,path=None):
        pygame.draw.circle(screen,self.color,(self.x,self.y),self.radius)
        screen.blit(self.text,self.textRect)
        for each in list(self.connectsTo.keys()):
            if path is not None and each in path and self in path:
                pygame.draw.line(screen,(255,0,255),(self.x,self.y),(each.x,each.y))
            else:
                pygame.draw.line(screen,(0,255,0),(self.x,self.y),(each.x,each.y))
def dist(v1,v2):
    return math.sqrt(pow(v2.x-v1.x,2)+pow(v2.y-v1.y,2)) if isinstance(v2,Point) else math.sqrt(pow(v2[0]-v1.x,2)+pow(v2[1]-v1.y,2))

def drawLines(l):
    for i,each in enumerate(l[1:]):
        pygame.draw.line(screen,(0,255,255),(l[i-1].x,l[i-1].y),(each.x,each.y))
        pygame.display.update()
        
def randomPathGenerator(points,paths):
    random.seed(42)
    for i in range(paths):
        valid = False
        pA = random.choice(points)
        while not valid:
            pB = random.choice(points)
            if pB != pA: 
                valid = True
        pA.connectsTo[pB] = dist(pA,pB)
        pB.connectsTo[pA] = dist(pA,pB)
        screen.fill((0,0,0))
        [each.update(path) for each in points]
        pygame.display.update()

##DEPTH FIRST,BREADTH FIRST,HILL CLIMBING AND BEAM SEARCH
class SearchAlgorithm():
    def __init__(self,startPoint,endpoint,currentMode):
        self.startPoint = startPoint
        self.endPoint = endpoint
        self.currentMode=currentMode
        self.beamWidth = 2
    def search(self):
        Queue = [[self.startPoint]]
        currentLevel = Queue
        LevelChange = False
        Reached = False
        extendedTo = []
        totalExtensions = 0
        while not Reached:
            clock.tick(20)
            for each in list(Queue[0][-1].connectsTo.keys()):
                x = copy.copy(Queue[0])
                if each in x or (each in extendedTo):
                    continue
                totalExtensions += 1
                x.append(each)
                Queue.append(x)
                if not Queue[0] in extendedTo:
                    extendedTo.append(Queue[0])
            del Queue[0]
            if self.currentMode == 'Depth First':
                Queue.sort(key=lambda x : x[-2].connectsTo[x[-1]])
            if self.currentMode == 'Hill Climbing':
                Queue.sort(key=lambda x : dist(x[-1],self.endPoint))
            if self.currentMode == 'Beam Search':
                for each in currentLevel:
                    levelChange=True
                    if each in Queue:
                        levelChange = False
                        break                    
                if LevelChange:
                    currentLevel= Queue
                    Queue.sort(key=lambda x : dist(x[-1],self.endPoint))
                    Queue = Queue[:self.beamWidth]
                    levelChange =False
            if Queue == []:
                print('No path found'); return None
            for i,each in enumerate(Queue):
                if each[-1] == self.endPoint:
                    bestPathInd = i
                    Reached = True
                    break
            screen.fill((0,0,0))
            [each.update(path) for each in points]
            drawLines(Queue[0])
            pygame.display.update()
            
        print(f'Current Mode: {self.currentMode}\nTotal Extensions: {totalExtensions}\nCurrent Queue Length: {len(Queue)}')
        print('the final path', [i.letter for i in Queue[0]])
        return Queue[bestPathInd]
            

##A* and BRANCH AND BOUND SEARCH
class OptimizedSearchAlgorithm():
    def __init__(self,startPoint,endpoint,currentMode):
        self.startPoint = startPoint
        self.endPoint = endpoint
        self.currentMode=currentMode
    def search(self):
        Queue = [[self.startPoint]]
        Reached = False
        extendedTo = []
        '''accumulated Distances'''
        amds= [0]
        '''accumulated Heuristic Distances'''
        amdsToSortFrom = [0]
        totalExtensions = 0
        while not Reached:
            clock.tick(20)
            for each in list(Queue[0][-1].connectsTo.keys()):
                x = copy.copy(Queue[0])
                if each in x or (each in extendedTo):
                    continue
                totalExtensions += 1
                amds.append(amds[0] + x[-1].connectsTo[each])
                amdsToSortFrom.append(amds[-1] + dist(each,self.endPoint))
                x.append(each)
                Queue.append(x)
                if not Queue[0] in extendedTo:
                    extendedTo.append(Queue[0])
            del Queue[0]
            del amds[0]
            del amdsToSortFrom[0]
            '''I am just solely going to do this with extended list'''
            if self.currentMode == 'BRANCH AND BOUND':
                print(Queue.index(Queue[0]),amds)
                Queue = sorted(Queue,key=lambda x : amds[Queue.index(x)])
                amds.sort()
            if self.currentMode == 'A*':
                Queue = sorted(Queue,key=lambda x : amdsToSortFrom[Queue.index(x)])
                amds=sorted(amds,key=lambda x :amdsToSortFrom[amds.index(x)])
                amdsToSortFrom.sort()
            if Queue == []:
                print('No path found')
                return None
            if Queue[0][-1] == self.endPoint:
                bestPathInd = 0
                Reached = True
                break
            screen.fill((0,0,0))
            [each.update(path) for each in points]
            drawLines(Queue[0])
            pygame.display.update()
            
        print(f'Current Mode: {self.currentMode}\nTotal Extensions: {totalExtensions}\nCurrent Queue Length: {len(Queue)}')
        print('the final path', [i.letter for i in Queue[0]])
        return Queue[bestPathInd]      

    
points = [Point() for i in range(26)]        
setEndpointsMode = False
modes = ['Depth First', 'Breadth First','Hill Climbing','Beam Search','BRANCH AND BOUND','A*']
optimizedAlgos = ['BANCH AND BOUND','A*']
currentMode = modes[0]
ModeNumber = 0
Endpoints = []
path = None
randomPathGenerator(points,23)
font = pygame.font.Font('freesansbold.ttf', 15) 

while run:
    text = font.render(currentMode, True, (255,255,255))
    textRect = text.get_rect()  
    textRect.center = (w//2, 6)
    
    
    screen.fill((0,0,0))
    screen.blit(text,textRect)
    [each.update(path) for each in points]
    pygame.display.update()
    
    for event in pygame.event.get():
        
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            state = 'disabled' if setEndpointsMode else 'enabled'
            print(f'setEndpointMode {state}')
            setEndpointsMode = True if not setEndpointsMode else False
        if keys[pygame.K_s]:
            if currentMode not in optimizedAlgos:
                searchAlgo = SearchAlgorithm(Endpoints[0],Endpoints[1],currentMode)
                path=searchAlgo.search()
            else:
                searchAlgo = OptimizedSearchAlgorithm(Endpoints[0],Endpoints[1],currentMode)
                path=searchAlgo.search()
        if keys[pygame.K_d]:
            ModeNumber += 1
            ModeNumber = 0 if ModeNumber >= len(modes) else ModeNumber
            currentMode = modes[ModeNumber]
        if keys[pygame.K_r]:
            for i in Endpoints:
                i.color=(255,255,255)
            Endpoints = []
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
            
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not setEndpointsMode:
                pointA = [i for i in points if dist(i, pygame.mouse.get_pos())<= 3]
                pointA = pointA[0] if pointA != [] else []
            else:
                Endpoint = [i for i in points if dist(i, pygame.mouse.get_pos())<= 3]
                if Endpoint != [] and Endpoint not in Endpoints and not len(Endpoints) == 2:
                    Endpoints.append(Endpoint[0])
                    print(Endpoints)
                    Endpoint[0].color = (255,0,0)
                
                
        if event.type == pygame.MOUSEBUTTONUP and not setEndpointsMode:
            pointB = [i for i in points if dist(i, pygame.mouse.get_pos())<= 3]
            pointB = pointB[0] if pointB != [] else []
            if not pointB == [] and not pointA == [] and not pointA == pointB:
                pointA.connectsTo[pointB] = dist(pointA,pointB)
                pointB.connectsTo[pointA] = dist(pointA,pointB)
