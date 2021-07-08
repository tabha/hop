import simpy
import random
from sympy.stats import Normal, sample_iter
SIM_TIME = 100000
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
# Maintenance scenarios
SCENARIOS =['MS1','MS2','MS3']
SCENARIOS_WEIGHT =[50,30,20]
data ={}
class TI(object):
    """
    this class represent a technical issue
    """
    def __init__(self, name_, weight_,interval_fail_list_):
        self.name = name_ # example : mechanical structural damage
        self.weight = weight_ # 0.3
        self.interval_fail_list_ = interval_fail_list_
        

    def run(self,env,data):
        #print(f"running {self.name}...")
        if not self.weight :
            return
        #weight is not null
        index = 0
        while True:
            interval_fail = self.interval_fail_list_[index]
            yield env.timeout(interval_fail/(self.weight)) # one part in this component fails
            #print(f"{self.name} has failed") 
            data[self.name]["occurence"] += 1
            index = (1+index) % len(self.interval_fail_list_) # to loop through the picked values
            #chose a maintenance scenarios
            ms = random.choices(SCENARIOS,SCENARIOS_WEIGHT,k=1)[0] # random.choices return a list
            try:
                data[self.name]["ms"][ms] += 1
            except:
                data[self.name]["ms"][ms] = 0

# this fonction initialize a list of random value (Normal distributions) for each type of ti,
# those inialized values can be later then be used as the interval of failure
def init_distributions(distributions_dic,samplessize):
    distributions = {} # a dictionnary of distribution which contains a list of random Normal values
    for ti in distributions_dic: # ti is the key in the distributions_dic
        mean = distributions_dic[ti]["mean"]
        std = distributions_dic[ti]["std"]
        distributions[ti] = list(sample_iter(Normal(ti,mean,std),numsamples=samplessize))
    return distributions

#this set up the tis 
def setup(env,tis,data,distributions_dic):
    print("creating technical issues")
    #create all technical issues and exec them
    distributions = init_distributions(distributions_dic,SAMPLES_SIZE)
    for ti in tis:
        print(f"{ti} creation...")
        obj_ti = TI(ti,tis[ti],distributions[ti])
        data[ti] = {"occurence":0,"ms":{}} # initialize the stats for this ti 
        env.process(obj_ti.run(env,data))
    yield env.timeout(1)


def show_stats(data):
    failures = 0
    for ti in data:
        failures += data[ti]['occurence']
        print(f'{ti} occured {data[ti]["occurence"]} times')
        for ms in data[ti]["ms"]:
            print(f'{ti} solved {data[ti]["ms"][ms]} times with {ms}')
    print(f"failures : {failures}, for simulation = {SIM_TIME}")


def main():
    env = simpy.Environment()
    env.process(setup(env,TIS,data,DISTRIBUTIONS))
    env.run(until=SIM_TIME)
    show_stats(data)


if __name__=='__main__':
    main()