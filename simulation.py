import simpy
import random

SIM_TIME = 10000

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


data ={}
class TI(object):
    """
    this class represent a technical issue
    """
    def __init__(self, name_, weight_,periodicity_):
        self.name = name_ # example : mechanical structural damage
        self.weight = weight_ # 0.3
        self.periodicity = periodicity_
        

    def run(self,env,data):
        #print(f"running {self.name}...")
        if not self.weight :
            return
        #weight is not null
        while True:
            yield env.timeout(100/(self.weight*self.periodicity)) # one part in this component fails
            #print(f"{self.name} has failed") 
            data[self.name] += 1
            
def setup(env,tis,data,periodicities):
    print("creating technical issues")
    #create all technical issues and exec them
    for ti in tis:
        print(f"{ti} creation...")
        obj_ti = TI(ti,tis[ti],periodicities[ti])
        data[ti] = 0 # initialize occurence 
        env.process(obj_ti.run(env,data))
    yield env.timeout(1)

env = simpy.Environment()
env.process(setup(env,TIS,data,PERIODICITIES))
env.run(until=SIM_TIME)
failures = 0
for ti in data:
    failures += data[ti]
print("Collected data ",data)
print(f"failures : {failures}, for simulation = {SIM_TIME}")
