import simpy
import random
from sympy.stats import Normal, sample_iter
SIM_TIME = 10000
SAMPLES_SIZE = 100
# INPUT for technical issues
TIS={
    'mechanical':0.25,
    'electrical':0.1,
    'electronic':0.3,
    'hydraulic':0.25,
    'pneumatic':0.5,
    'other':0.5
}
# Periodicity for each type of issues
PERIODICITIES={
    'mechanical':100,
    'electrical':25,
    'electronic':50,
    'hydraulic':15,
    'pneumatic':20,
    'other':10
}
# Discrituion for each type of failue this type we are using a Normal distribution
DISTRIBUTIONS ={
    'mechanical':{"mean":10,"std":2},
    'electrical':{"mean":20,"std":3},
    'electronic':{"mean":40,"std":10},
    'hydraulic':{"mean":50,"std":5},
    'pneumatic':{"mean":5,"std":1},
    'other':{"mean":10,"std":2}
}

data ={}
class TI(object):
    """
    this class represent a technical issue
    """
    def __init__(self, name_, weight_,distribution_list_):
        self.name = name_ # example : mechanical structural damage
        self.weight = weight_ # 0.3
        self.distribution_list = distribution_list_
        

    def run(self,env,data):
        #print(f"running {self.name}...")
        if not self.weight :
            return
        #weight is not null
        index = 0
        while True:
            interval_fail = self.distribution_list[index]
            yield env.timeout(interval_fail/(self.weight)) # one part in this component fails
            #print(f"{self.name} has failed") 
            data[self.name] += 1
            index = (1+index) % len(self.distribution_list)
# this fonction initialize a list of random value (Normal distributions) for each type of ti,
# those inialized values can be later then be used as the interval of failure
def init_distributions(distributions_dic,samplessize):
    distributions = {} # a dictionnary of distribution which contains a list of random Normal values
    for ti in distributions_dic: # ti is the key in the distributions_dic
        mean = distributions_dic[ti]["mean"]
        std = distributions_dic[ti]["std"]
        distributions[ti] = list(sample_iter(Normal(ti,mean,std),numsamples=samplessize))
    return distributions

#this set up the ti 
def setup(env,tis,data,distributions_dic):
    print("creating technical issues")
    #create all technical issues and exec them
    distributions = init_distributions(distributions_dic,SAMPLES_SIZE)
    for ti in tis:
        print(f"{ti} creation...")
        obj_ti = TI(ti,tis[ti],distributions[ti])
        data[ti] = 0 # initialize occurence 
        env.process(obj_ti.run(env,data))
    yield env.timeout(1)

env = simpy.Environment()
env.process(setup(env,TIS,data,DISTRIBUTIONS))
env.run(until=SIM_TIME)
failures = 0
for ti in data:
    failures += data[ti]
print("Collected data ",data)
print(f"failures : {failures}, for simulation = {SIM_TIME}")
