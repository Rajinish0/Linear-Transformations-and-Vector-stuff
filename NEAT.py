import numpy as np
import torch.nn as nn
import torch,copy
import random


class setup:
    def __init__(self,class_,inputFeatures,target,max_pop = 150,mutation_rate=.01):
        #self.X = X
        #self.Y = Y
        self.target = target
        self.inputFeatures = inputFeatures
        self.max_pop = max_pop
        self.mutation_rate = mutation_rate
        self.population = Population().generate(self.max_pop, self.target,class_,self.inputFeatures)
        self.prev_pop = None
        self.fitness = self.calc_fitness()
        self.prev_fitness = None
        self.class_ = class_
    def calc_fitness(self):
        fitness = []
        for i in self.population:
            print(i.score)
            fitness.append(i.score)
           # pred = i.network(X)
           # pred[pred>=.5] = 1
           # pred[pred<.5]=0
           # fitness.append(self.calc_accuracy(pred,Y).item())
        #for each in range(len(fitness)):
          #  print(sum(fitness))
         #   fitness[each] = fitness[each]/sum(fitness) if sum(fitness) >0 else fitness[each]
       # print(fitness)
        return fitness
    def calc_accuracy(self,X_train, y_train):
        pass
        #train_acc = (1 - torch.mean(torch.abs(y_train - X_train))) * 100
        #return train_acc
        #print('Train set accuracy: {} %'.format(int(train_acc)))
    def acceptReject(self):
        safety = 0
        while True:
            i = random.randint(0,self.max_pop-1)
            r = random.choice(self.fitness)
            #print(len(self.fitness))
            if random.random() < self.fitness[i]:
                return self.population[i].network
            safety += 1
            if safety > 50000:
                print('uh oh')
                break
    def reproduce(self,):
        self.prev_fitness = self.fitness
        self.fitness= self.calc_fitness()
        total = sum(self.fitness)
        self.fitness = [each/total for each in self.fitness]
        print('MAX FITNESS', max(self.fitness))
        # if sum(self.fitness)/self.max_pop < sum(self.prev_fitness)/self.max_pop:
           # if self.prev_pop is not None:
               # print('GOING BACK HOMIE')
               # self.population =self.prev_pop
               # self.fitness = self.prev_fitness
                
        population = []
#         if max(self.fitness) >= 60:
        # a = self.population[self.fitness.index(max(self.fitness))].network
        # l = copy.copy(self.fitness)
        # l.remove(max(l))
        # b = self.population[l.index(max(l))+1].network
        for i in range(self.max_pop):
#             if max(self.fitness)<60:
            a = self.acceptReject()
            b = self.acceptReject()
            child = DNA(1,False,self.class_)
            child.network = self.crossover(a,b)
            self.mutate(child.network,self.mutation_rate)
            population.append(child)
        #self.prev_pop = self.population
        return population
    def mutate(self,child,mutation_rate):
        for i in range(len(child)):
            if not isinstance(child[i],nn.Linear):
   #             l.append(child[i])
                continue
            with torch.no_grad():
                self.apply_mutation(child[i].weight,mutation_rate,False)
                self.apply_mutation(child[i].bias,mutation_rate,True)
    def apply_mutation(self,x,r,bias):
        l = [1, -1]
        if bias:
            for i in range(len(x)):
                if random.random() < r:
                    x[i] += random.choice(l)*random.random()
        else:
            for i in range(len(x)):
                for j in range(len(x[0])):
                    if random.random() < r:
                        x[i][j] += random.choice(l)*random.random()
                
    def crossover(self, a, b):
        l = []
        for i in range(len(a)):
            if not isinstance(a[i],nn.Linear):
                l.append(a[i])
                continue
            with torch.no_grad():
                total = a[i].weight.shape[1]
                total2 = a[i].bias.shape[0]
                new = nn.Linear(a[i].weight.shape[1],a[i].weight.shape[0])
                mid_point = random.randint(0,total)
                mid_point2 = random.randint(0,total2)
                new.weight[:,:mid_point] = a[i].weight[:,:mid_point]
                new.weight[:,mid_point:] = b[i].weight[:,mid_point:]
                new.bias[:mid_point2] = a[i].bias[:mid_point2]
                new.bias[mid_point2:] = b[i].bias[mid_point2:]
                l.append(new)
               # print(new.weight.shape, new.bias.shape)
        return nn.Sequential(*l)
    def go(self):
        for i in range(100):
            print(max(self.fitness))
            self.population = self.reproduce()
            self.fitness = self.calc_fitness(self.X,self.Y)


class Population():
    def __init__(self):
        pass
    def generate(self,max_pop,target,class_,inputFeatures):
        population = []
        for i in range(max_pop):
            population.append(DNA(target,True,class_,inputFeatures))
        return population

class DNA():
    def __init__(self,target,random_,class_,inputFeatures=None):
        self.target = target
        self.inputFeatures = inputFeatures
        self.network = self.generate(target) if random_ else None
        self.phenotype = class_()
        self.phenotype.UpdateAngle(270)
        self.score = 0
        self.totaltimesurvived = 0
    def generate(self,target):
        return nn.Sequential(nn.Linear(self.inputFeatures,14),
                      		nn.ReLU(),
                      		nn.Linear(14,target),
                    		#nn.ReLU(),
                    		#nn.Linear(12,target),
                            nn.Softmax(1))
