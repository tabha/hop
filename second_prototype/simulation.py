import simpy
import random
import json
from sympy.stats import Normal, sample_iter, LogNormal



"""
mt-> maintenance
aw-> airworthiness
perf-> performance

md ={
    "mt-flexibility":
}
"""
class ATA2D(Object):
    """
    ti_params=[
        {
            "name":"Periodicity",
            "type":"Normal",
            "mean":50,
            "std":30
        },{
            "name":"Report-phase",
            "type":"BFP",
            "weights":[0.2,0.5,0.3]
        }
        ...
    ]
    """
    def __init__(self,params,CLASSES):
        self.parameters = []
        
        for param in params:
            self.parameters.append(Parameter(param,CLASSES))
    def choose_ms(self,md):
        """
            return the mainteance scenario
            implment the logic, how a mainteance scenario is choosed
        """
        return {}
    def run(self,env,data):
        tis = data["tis"]
        ms = data["ms"]
        mds =data["mds"]
        while True:
            ti=[]
            for p in self.parameters:
                ti.append(p.random_choices(k=1)) # add {"name":"Peridicity","value":randomly_choosed_value}
            index = 0
            # find the periodicity param
            for p in ti:
                if p.name=="Periodicity":
                    break
                index +=1
            yield env.timeout(ti[index].value)
            # add the ti in the list of tis
            tis.append(ti)
            # generated the maintenance demand based on the ti
            md = MaintenanceDemand(ti).getDemand()
            # choose the maintenance scenario
            ms.append(self.choose_ms(md))
            mds.append(md)



        

class MaintenanceDemand(Object):

    def __init__(self,ti_param_list):
        self.occured_ti = ti_param_list

    def  getDemand(self)
        # this function implements all the logic 
        # how a mainteance demand is generated
        # base on the ti
        return "return the generated mainteance demand a list of parameters"


class Parameter:

    """
    Supported typeDistribution are
    LMH for Low medium high
    BIN for Binary distribution only two classes
    NORMAL for parameter that folows normal distributions
    LOG for parameters that follows Log normal distributions
    mean and std are only used for Normal and LOG typesDistributions
    """
    def __init__(self,params,CLASSES):
        self.name = params["name"]
        self.typeDistribution = params["type"]
        if params.has_key("mean") and params.has_key("std"):
            # only Log and log Noraml parameters has mean and std key defined
            self.mean=params["mean"]
            self.std=params["std"]
        else if params.has_key("weights"):
            self.classes = CLASSES[self.typeDistribution]
            self.weights = params["weights"]
    
    """
    return one value picke randomly based on the parameter type
    """
    def random_choices(self,k=1)
        if(self.typeDistribution=="NORMAL"):
            return list(
                sample_iter(
                    Normal(
                        self.name,
                        self.mean,
                        self.std
                    ),
                    numsamples=1
                )
            )[0]
        if self.typeDistribution=="LOG":
            return list(
                sample_iter(
                    LogNormal(
                        self.name,
                        self.mean,
                        self.std
                    ),
                    numsamples=1
                )
            )[0] 
        ## for LMH or BIN
        result = random.choices(
            self.classes,
            self.weights
        )[:k-1]
        return {
            "name":self.name,
            "value":result
        }


def setup(env,data,sim_params):
    parameters = sim_params["ATA2D"]["ti_parameters"]
    ata2D_aircondition = ATA2D(parameters)
    data["tis"] =[] # collect all tis
    data["mds"] =[] # collect all mainteance demand
    data["ms"]  =[] # collect all maintenance scenarios
    env.process(ata2D_aircondition.run(env,data))
    yield env.timeout(1)


def show_stats(data,SIM_TIME):


def main():
    f = open("parameters.json")
    sim_params = json_load(f)
    env = simpy.Environment()
    env.process(setup(env,data,sim_params))
    env.run(until=sim_params["sim_time"])
    show_stats(data,sim_params["sim_time"])