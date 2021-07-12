import simpy
import random
import json
from sympy.stats import Normal, sample_iter

data ={}
class TI(object):
    """
    this class represent a technical issue
    """
    def __init__(self, ti_obj):
        self.name = ti_obj["name"] # example : mechanical structural damage
        self.weight = ti_obj["weight"] # 0.3
        self.distribution = ti_obj["distribution"]
        self.scenarios = ti_obj["ms"]
        

    def chose_scenario(self):
        ms = random.choices(
                    [scenario["name"] for scenario in self.scenarios],
                    [scenario["weight"] for scenario in self.scenarios],
                    k=1
                )[0]
        return ms

    def run(self,env,data):
        #print(f"running {self.name}...")
        if not self.weight :
            return
        #weight is not null
        index = 0
        while True:
            
            interval_fail = list(
                                sample_iter(
                                    Normal(
                                        self.distribution["name"],
                                        self.distribution["params"]["mean"],
                                        self.distribution["params"]["std"]
                                    ),
                                    numsamples=1)
                                ) [0]
            yield env.timeout(interval_fail/(self.weight)) # one part in this component fails
            #print(f"{self.name} has failed") 
            data[self.name]["occurence"] += 1
            #chose a maintenance scenarios
            ms = self.chose_scenario()
            try:
                data[self.name]["ms"][ms] += 1 #stats
            except:
                data[self.name]["ms"][ms] = 0


#this set up the tis 
def setup(env,data,config):
    print("creating technical issues")
    #create all technical issues and exec them
    #distributions = init_distributions(distributions_dic,SAMPLES_SIZE)
    for ti in config["tis"]:
        print(f"{ti['name']} creation ")
        obj_ti = TI(ti)
        data[ti["name"]] ={"occurence":0,"ms":{}} 
        env.process(obj_ti.run(env,data))    
    
    yield env.timeout(1)


def show_stats(data,sim_time):
    failures = 0
    for ti in data:
        failures += data[ti]['occurence']
        print(f'{ti} occured {data[ti]["occurence"]} times')
        for ms in data[ti]["ms"]:
            print(f'{ti} solved {data[ti]["ms"][ms]} times with {ms}')
    print(f"failures : {failures}, for simulation = {sim_time}")


def read_config(path):
    f = open(path)
    config = json.load(f)
    return config

def main():
    config = read_config('simulation.json')
    #print('Config :',config)
    env = simpy.Environment()
    env.process(setup(env,data,config))
    env.run(until=config["sim_time"])
    show_stats(data,config["sim_time"])


if __name__=='__main__':
    main()