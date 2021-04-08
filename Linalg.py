import math,copy
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
    @property
    def npV(self):
        return np.array([*self.elems]).reshape(-1,1)
    


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
            raise Exception("Gotta be a vector hombre {}".format(b))
        try:
            return Vector(*[(self[i] + b[i]) for i in range(len(self))])
        except:
            raise Exception("dims don't match man {}d and {}d".format(len(self),len(b)))


    def applyTransformation(self,mat,return_new=False):
        if not isinstance(mat,Matrix):
            raise Exception('ffs man, necessito un matrix.')
        try:
            if len(mat) != len(self.elems):
                raise Exception;

            return Vector(*list((mat.npMAT@self.npV)[:,0]))
            # return (reduce(lambda x,y :x+y,[(mat[i]*self[i]) for i in range(len(self))]))
        except:
            raise Exception(f"{len(self)}d vector with a {len(mat[0])}x{len(mat)} Matrix, '\n\n' {self}\n\n {mat}")

        # self.elems = transformed.elems if not return_new else self.elems
        # return self if not return_new else transformed


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

    ##2D rotation
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


    def RotationOnX(self,angle):
        m = Matrix([[1,0,0],
                [0,math.cos(math.radians(angle)),-math.sin(math.radians(angle))],
                [0,math.sin(math.radians(angle)),math.cos(math.radians(angle))]])
        return m
    def RotationOnY(self,angle):
        m = Matrix([
                [math.cos(math.radians(angle)),0,-math.sin(math.radians(angle))],
                [0,1,0],
                [math.sin(math.radians(angle)),0,math.cos(math.radians(angle))]
                ])  
        return m
    def RotationOnZ(self,angle):
        m = Matrix([
                [math.cos(math.radians(angle)),-math.sin(math.radians(angle)),0],
                [math.sin(math.radians(angle)),math.cos(math.radians(angle)),0],
                [0,0,1]
                ])
        return m

    ##3D rotations
    def RotationX(self,angle,center,return_new=True):
        return self.Gen3dRotation(self.RotationOnX(angle),center,return_new)
    def RotationY(self,angle,center,return_new=True):
        return self.Gen3dRotation(self.RotationOnY(angle),center,return_new)
    def RotationZ(self,angle,center,return_new=True):
        return self.Gen3dRotation(self.RotationOnZ(angle),center,return_new)

    def Gen3dRotation(self,mat,center,return_new = True):
        origElems = copy.copy(self.elems)
        self.elems = [self[i]-center[i] for i in range(len(self))]

        transformation = self.applyTransformation(mat)
        self.elems = [center[i]+transformation[i] for i in range(len(self))]
        rotated = self.elems


        self.elems = origElems if return_new else self.elems
        return self if not return_new else Vector(*rotated)



    def GetMagnitude(self, sqrt=True):
        mag = (sum([pow(elem,2) for elem in self.elems]))
        return math.sqrt(mag) if sqrt else mag

    def __mul__(self,scl):
        if isinstance(scl,Vector):
            return self.dot(b)
        return Vector(*[self[i]*scl for i in range(len(self))])

    def __rmul__(self,scl):
        return self.__mul__(scl)
    #__rmul__= __mul__



    def __truediv__(self,scl):
        return Vector(*[self[i]/scl for i in range(len(self))])


    def __sub__(self,b):
        res = self.__add__(-1*b)
        return res

    def __eq__(self,other):
        return reduce(lambda x,y: x and y, [self[i] == other[i] for i in range(len(self))]) if other is not None else False


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

        if type(twoDList[0]) == list or type(twoDList) == np.ndarray:
            try:
                validLen = len(twoDList[0])
            except:
                validLen = 1


            self.npMAT = np.array(twoDList)
            try:
                twoDList= [list(x) for x in self.npMAT.T]
            except:
                twoDList = [[x] for x in self.npMAT.T]


            prev = None
            for each in twoDList:
                if prev is not None and len(each) != len(prev):
                    raise Exception('dims don\'t match {}d and {}d.'.format((prev),(each)))
                v = Vector(*each)
                self.mat.append(v)
                prev = v

        elif type(twoDList[0]) == Vector:
            self.mat = twoDList
            self.npMAT = Matrix.GenerateNpMat(twoDList)
            assert reduce((lambda x,y: x and y), [(type(each) == Vector) for each in twoDList])

        else:
            raise Exception(f'wdf are you sending me. {type(twoDList[0])}')


    @property
    def shape(self):
        return Vector(len(self.mat[0]),len(self.mat))
    
    def __repr__(self):
        return f'MATRIX {self.mat}'

    def __mul__(self,scl):
        return Matrix([self[i]*scl for i in range(len(self))])
    __rmul__ = __mul__

    def __add__(self,b):
        return Matrix([self[i]+b[i] for i, each in enumerate(self)])

    def __sub__(self,b):
        return self + (b*-1)

    def __getitem__(self,i):
        return self.mat[i]

    def __len__(self):
        return len(self.mat)
    
    def inv(self):
        return np.linalg.inv(self.npMAT)

    def applyTransformation(self,mat):
        if type(mat) != Matrix:
            mat = Matrix(mat)
        try:
            return Matrix([self[i].applyTransformation(mat) for i in range(len(self))])
        except:
            raise Exception(f"{len(self)}x{len(self[0])} with {len(mat)}x{len(mat[0])}, you loco man.")



    def calcDeterminent(self,mat=None):
        mat = self.npMAT if mat is None else mat
        assert type(mat) == np.ndarray

        if not reduce(lambda x,y: x == y, [each for each in mat.shape]):
            raise Exception(f"NOT A SQUARE MATRIX, PUTA MADRE. SHAPE: {mat.shape}")

        if len(mat[0]) == 1:
            return mat.item()


        det = 0
        for i in range(len(mat[0])):
            num = mat[0][i]
            nMat = mat[1:]
            rMat = np.c_[nMat[:,:i],nMat[:,i+1:]]
            det += pow(-1,1+i+1) * num * self.calcDeterminent(rMat)
        return det

    @staticmethod
    def GenerateNpMat(twoDList):
        return np.array([each.elems for each in twoDList]).T


