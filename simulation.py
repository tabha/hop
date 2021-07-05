import simpy
import random

TIS={
    'mechanical':0.25,
    'electrical':0.1,
    'electronic':0.3,
    'hydraulic':0.25,
    'pneumatic':0,
    'other':0.1
}

data ={}
class TI(object):
    """
    this class represent a technical issue
    """
    def __init__(self, name_, weight_):
        self.name = name_ # example : mechanical structural damage
        self.weight = weight_ # 0.3
        

    def run(self,env,data):
        #print(f"running {self.name}...")
        if not self.weight :
            return
        #weight is not null
        while True:
            yield env.timeout(1.0/self.weight)
            #print(f"{self.name} has failed") 
            data[self.name] += 1
            
def setup(env,tis,data):
    print("creating technical issues")
    #create all technical issues and exec them
    for ti in tis:
        print(f"{ti} creation...")
        obj_ti = TI(ti,tis[ti])
        data[ti] = 0 # initialize occurence 
        env.process(obj_ti.run(env,data))
    yield env.timeout(1)

env = simpy.Environment()
env.process(setup(env,TIS,data))
env.run(until=100)

print("Collected data ",data)
