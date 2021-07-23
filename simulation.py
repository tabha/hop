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
        self.reporting_phase = ti_obj["reporting_phase"]
        self.ti = ti_obj
        
    """
    def chose_scenario(self):
        ms = random.choices(
                    [scenario["name"] for scenario in self.scenarios],
                    [scenario["weight"] for scenario in self.scenarios],
                    k=1
                )[0]
        return ms
    """
    def chose_scenario(self,aw_impact,perf_impact,config):
        """
        define the rule how to pick a ms
        """
        score = (config["aw_impact_weight"]*config["aw_scores"][aw_impact]) + (config["perf_impact_weight"]*config["perf_scores"][perf_impact])
        index = 2 # by default it is LOW
        if score > 2 :
            index = 0 # HIGH
        elif score < 2 and score > 1:
            index = 1 # MEDIUM
        impact = config["impact_scores"][index] # HIGH, MEDIUM OR LOW
        ms = random.choices(
            config["ms_rules"]["ms"], # MS1 , MS2 or MS3
            config["ms_rules"][impact], # WEIGHTS
            k=1,
        )[0]
        return ms,impact
        
    def find_reporting_phase(self):
        phase = random.choices(
            [phase["name"] for phase in self.reporting_phase],
            [phase["weight"] for phase in self.reporting_phase],
            k=1,
        )[0]
        return phase
    def impact(self):
        # chose the airworthiness GO NOGO GOIF
        
        aw = random.choices(
            [aw["name"] for aw in self.ti["airworthines_impact"]],
            [aw["weight"] for aw in self.ti["airworthines_impact"]]
        )[0]
        # choose the performance impact HIGH, LOW or Midium
        perf = random.choices(
            [perf["name"] for perf in self.ti["performance_impact"]],
            [perf["weight"] for perf in self.ti["performance_impact"]]
        )[0]
        return aw,perf
    def run(self,env,data,config):
        #print(f"running {self.name}...")
        tis_report = data["tis"]
        ac_report = data["ac_impact"]
        if not self.weight :
            return
        #weight is not null
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
            tis_report[self.name]["occurence"] += 1

            # find the reporting phase
            phase = self.find_reporting_phase()
            try:
                tis_report[self.name]["phases"][phase] += 1
            except:
                tis_report[self.name]["phases"][phase] = 1
            # compute the impact
            aw_impact,perf_impact = self.impact()
            ms,ac_impact = self.chose_scenario(aw_impact,perf_impact,config)
            #print(f"{self.name} has failed") 
            #chose a maintenance scenarios
            #ms = self.chose_scenario()
            try:
                tis_report[self.name]["ms"][ms] += 1 #stats
            except:
                tis_report[self.name]["ms"][ms] = 1
            try:
                ac_report[ac_impact] += 1 #stats
            except:
                ac_report[ac_impact] = 1 #stats

                        


#this set up the tis 
def setup(env,data,config):
    print("creating technical issues")
    #create all technical issues and exec them
    #distributions = init_distributions(distributions_dic,SAMPLES_SIZE)
    data["ac_impact"] = {}
    data["tis"] = {}
    for ti in config["tis"]:
        print(f"{ti['name']} creation ")
        obj_ti = TI(ti)
        data["tis"][ti["name"]] ={
            "occurence":0,
            "ms":{},
            "phases":{}
        } 
        env.process(obj_ti.run(env,data,config))    
    
    yield env.timeout(1)


def show_stats(data,sim_time):
    failures = 0
    tis_report = data["tis"]
    for ti in data["tis"]:
        print(ti)
        failures += tis_report[ti]["occurence"]
        print(f'{ti} occured {tis_report[ti]["occurence"]} times')
        for ms in tis_report[ti]["ms"]:
            print(f'{ti} solved {tis_report[ti]["ms"][ms]} times with {ms}')
        for phase in tis_report[ti]["phases"]:
            print(f'{ti} reported {tis_report[ti]["phases"][phase]} times int {phase} phase')
    print(f"failures : {failures}, for simulation = {sim_time}")
    print("Aircraft impact ")
    for ac_imp in data["ac_impact"]:
        print(f"STATE : {ac_imp} {data['ac_impact'][ac_imp]} times")


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