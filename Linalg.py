import math
import numpy as np
from functools import reduce

class Vector():
    def __init__(self,*args):
        self.elems = [i for i in args]

    @property    
    def x(self):
        return self.elems[0]
    @property
    def y(self):
        return self.elems[1]
    @property
    def z(self):
        return self.elems[2]
     

    @x.setter
    def x(self,val):
        self.elems[0] = val
    @y.setter
    def y(self,val):
        self.elems[1] = val
    @z.setter
    def z(self):
        self.elems[2] = val


    def normalized(self):
        magnitude = self.GetMagnitude()
        if not magnitude == 0:
            args = [(elem/magnitude) for elem in self.elems]
            return Vector(*args)
        else:
            return Vector(0,0)            

    def __repr__(self):
        return ('Vector {}'.format(self.elems))

    def __getitem__(self,ind):
        return self.elems[ind]

    def __len__(self):
        return len(self.elems);

    def __add__(self,b):
        if not isinstance(b,Vector):
            raise Exception("Gotta be a vector hombre")
        try:
            return Vector(*[(self[i] + b[i]) for i in range(len(self))])
        except:
            raise Exception("dims don't match man {}d and {}d".format(len(self),len(b)))


    def applyTransformation(self,mat):
        if not isinstance(mat,Matrix):
            raise Exception('ffs man')
        return reduce(lambda x,y :x+y,[self[i]*mat[i] for i in range(len(self))])


    def elem_product(self,b):
        if not isinstance(b,Vector):
            raise Exception('nvm too tired to write this') 
        return Vector(*[self[i]*b[i] for i in range(len(self))])


    def dot(self,b):
        return reduce(lambda x,y :x+y,[self[i]*b[i] for i in range(len(self))])


    def SetMag(self,mag):
        new = self.normalized()*mag
        self.elems = new.elems
        return self

    def heading(self,deg=True):
        norm = self.normalized()
        return np.angle(np.array([complex(norm.x,norm.y)]),deg)[0]

    def rotate(self,center,angle):
        '''can define a rotation matrix for this um [[cosx, -sinx],
                                                     [sinx,cosx]] * [[x]]
                                                                     [y]]'''
        self.elems = [self[i]-center[i] for i in range(len(self))]
        #newX = self.x*math.cos(math.radians(angle)) - self.y*math.sin(math.radians(angle))
        #newY = self.y*math.cos(math.radians(angle)) + self.x*math.sin(math.radians(angle))
        rotationMatrix = Matrix([[math.cos(math.radians(angle)),-1*math.sin(math.radians(angle))],
                                [math.sin(math.radians(angle)),math.cos(math.radians(angle))]])
        transformation = self.applyTransformation(rotationMatrix)
        self.elems = [center[i]+transformation[i] for i in range(len(self))]
        return self
    def GetMagnitude(self):
        return math.sqrt(sum([pow(elem,2) for elem in self.elems]))

    def __mul__(self,scl):
        if isinstance(scl,Vector):
            return self.dot(b)
        return Vector(*[self[i]*scl for i in range(len(self))])


    __rmul__= __mul__


    def __truediv__(self,scl):
        return Vector(*[self[i]/scl for i in range(len(self))])


    def __sub__(self,b):
        return self.__add__(b*-1)

    def __eq__(self,other):
        return reduce(lambda x,y: x and y, [self[i] == other[i] for i in range(len(self))])

    @staticmethod
    def up():
        return Vector(0,-1)
    @staticmethod
    def GetDist(v1,v2):
        return math.sqrt(reduce(lambda x,y: x+y, [pow(v1[i]-v2[i],2) for i in range(len(v2))]))
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
