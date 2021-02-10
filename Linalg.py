import math
import numpy as np

class Vector():
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.mag = self.GetMagnitude()
        #self.npVector = np.array([np.complex(norm.x,norm.y)])
    def normalized(self):
        magnitude = math.sqrt((pow(self.x,2))+pow(self.y,2))
        if not magnitude == 0:
            return Vector(self.x/magnitude,self.y/magnitude)
        else:
            return Vector(0,0)


    def __repr__(self):
        return ('Vector {}'.format(list((self.x,self.y))))


    def __add__(self,b):
        if not isinstance(b,Vector):
            raise Exception("Gotta be a vector hombre")
        return Vector(self.x+b.x,self.y+b.y)


    def applyTransformation(self,mat):
        if not isinstance(mat,Matrix):
            raise Exception('ffs man')
        return self.x*mat[0] + self.y*mat[1]


    def elem_product(self,b):
        if not isinstance(b,Vector):
            raise Exception('nvm too tired to write this')
        return Vector(self.x*b.x,self.y*b.y)


    def dot(self,b):
        return (self.x*b.x) + (self.y*b.y)


    def SetMag(self,mag):
        new = self.normalized()*mag
        self.x,self.y = new.x,new.y
        return self

        
    def SetDirection(self,direc):
        self = self.normalized().elem_product(direc)*self.GetMagnitude()
        return self

    def heading(self,deg=True):
        norm = self.normalized()
        return np.angle(np.array([complex(norm.x,norm.y)]),deg)[0]

    def rotate(self,center,angle):
        '''can define a rotation matrix for this um [[cosx, -sinx],
                                                     [sinx,cosx]] * [[x]]
                                                                     [y]]'''
        self.x,self.y = self.x-center.x,self.y-center.y
        #newX = self.x*math.cos(math.radians(angle)) - self.y*math.sin(math.radians(angle))
        #newY = self.y*math.cos(math.radians(angle)) + self.x*math.sin(math.radians(angle))
        rotationMatrix = Matrix([[math.cos(math.radians(angle)),-1*math.sin(math.radians(angle))],
                                [math.sin(math.radians(angle)),math.cos(math.radians(angle))]])
        transformation = self.applyTransformation(rotationMatrix)
        self.x,self.y = transformation.x+center.x,transformation.y+center.y
        return self
    def GetMagnitude(self):
        return math.sqrt((pow(self.x,2))+pow(self.y,2))


    def __mul__(self,scl):
        if isinstance(scl,Vector):
            return (self.x*scl.x)+(self.y*scl.y)
        return Vector(self.x*scl,self.y*scl)


    __rmul__= __mul__


    def __truediv__(self,scl):
        return Vector(self.x/scl,self.y/scl)


    def __sub__(self,b):
        return self.__add__(b*-1)

    def __eq__(self,other):
        return (abs(self.x-other.x)<.01 and abs(self.y-other.y)<.01)

    @staticmethod
    def up():
        return Vector(0,-1)
    @classmethod
    def GetDist(cls,v1,v2):
        return math.sqrt((pow(v2.x-v1.x,2))+pow(v2.y-v1.y,2))
    @staticmethod
    def down():
        return Vector(0,1)
    @staticmethod
    def left():
        return Vector(-1,0)
    @staticmethod
    def right():
        return Vector(1,0)


## I PROBABLY SHOULD MAKE THIS COMPATIBLE WITH NUMPY..
class Matrix():
    def __init__(self,twoDList):
        self.mat = []
        validLen = len(twoDList[0])
        self.npMAT = np.array(twoDList)
        twoDList= [list(x) for x in np.array(twoDList).T]
        for each in twoDList:
            if len(each) != validLen:
                raise Exception('You know the drill')
            self.mat.append(Vector(*each))
    def __repr__(self):
        return f'MATRIX {self.mat}'
    def __getitem__(self,i):
        return self.mat[i]
    
    def inv(self):
        return np.linalg.inv(self.npMAT)

