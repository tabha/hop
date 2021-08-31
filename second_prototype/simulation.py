import simpy
import random
import json
from sympy.stats import Normal, sample_iter, LogNormal
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
"""
In this phase
an ATA2D we are no longer simulating all tis,
but only the behavior of an ATA2D.
which can be defined as a list of probabilistic parameters,
at each step of the simulation, we have to chose de value of these paramas
probabilistcally.
Question : ALL Params are independents?
"""
class ATA2D(object):
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
        for param in params: # Go through all params an initialize them as Parameter objects
            self.parameters.append(Parameter(param,CLASSES))
    def choose_ms(self,ti_parameters,sim_params):
        """
            return the mainteance scenario
            implment the logic, how a mainteance scenario is choosed
        """
        perf_impact=""
        aw_impact=""
        report_phase=""
        for p in ti_parameters:
            if p["name"]=="perf-impact":
                perf_impact=p["value"]
            elif p["name"]=="aw-status":
                aw_impact=p["value"]
            elif p["name"]=="Report-phase":
                report_phase=p["value"]
            if perf_impact and aw_impact and report_phase:
                break
        perf_score = sim_params["perf_scores"][perf_impact]
        aw_score =sim_params["aw_scores"][aw_impact]
        report_phase_score = sim_params["report_phase_scores"][report_phase]
        score = (sim_params["aw_impact_weight"]*aw_score)+(sim_params["perf_impact_weight"]*perf_score)+(sim_params["report_impact_weight"]*report_phase_score)
        #print(f'Values : perf_impact={perf_impact} aw_impact={aw_impact} report_phase={report_phase}')
        #print(f'SCORE : {score}, perf_score={perf_score} report_score={report_phase_score} aw_score={aw_score}')

        index = 2 # by default it is LOW
        if score > 2 : # 3
            index = 0 # HIGH
        elif score < 2 and score > 1: # 3 2
            index = 1 # MEDIUM
        impact=sim_params["impact_scores"][index] # HIGH , MEDIUM , LOW
        ms = random.choices(
            sim_params["ms_rules"]["ms"], # ["MS1","MS2","MS3","MS4"]
            sim_params["ms_rules"][impact]
        )[0]
        return {
            "impact": impact,
            "scenario":ms
        }
    def run(self,env,data,sim_params):
        tis = data["tis"]
        ms = data["ms"]
        mds =data["mds"]
        iterations=data["iterations"]
        iteration=1
        while True:
            ti=[] # a ti is a defined as a set of paramaters
            for p in self.parameters:
                ti.append(p.random_choice()) # add {"name":"Peridicity","value":randomly_choosed_value}
            index = 0
            # find the periodicity param
            for p in ti:
                if p["name"]=="Periodicity":
                    break
                index +=1
            yield env.timeout(ti[index]["value"]) # a failure of an ATA2D
            # add the ti in the list of tis
            tis.append(ti)
            # choose the maintenance scenario
            scenario = self.choose_ms(ti,sim_params)
            ms.append(scenario)
            # generated the maintenance demand based on the ti
            mds_params = MaintenanceDemand(scenario).getDemand(sim_params)
            mds.append(mds_params) # [[{"MD1":".."},{"MD2"}]]
            # add data to iterations
            iterations.append(
                {
                    "iteration":f'{iteration}',
                    "ti_parameters":ti, # the ti that occured
                    "md_parameters":mds_params, # the md parameters list
                    "scenario":scenario # the scenario choosed to solve the ti
                }
            )
            iteration +=1


class MaintenanceDemand(object):

    def __init__(self,scenario):
        self.scenario = scenario
    def  getDemand(self,sim_params):
        # this function implements all the logic 
        # how a mainteance demand is generated
        # base on the ti
        # scenario is like {"impact":"HIGH","ms":"MS2"}
        md_list = sim_params["MS"][self.scenario["scenario"]] # ["MD1","MD3"]
        mds_params = {}
        for md in md_list:
            # Get the params configuration for this MD
            paramList = sim_params["MD"][md]["parameters"]
            mds_params[md] = [] # each MD hold a list of simulated params
            for p in paramList: # go through all the parameters for this md
                mds_params[md].append(
                        Parameter(p,sim_params["classes"]).random_choice()
                    )
        # mds_params=[{"MD1":["list of parameters for MD1 randomly choosed"]},...]
        return mds_params
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
        if ("mean" in params) and ("std" in params):
            # only Log and log Noraml parameters has mean and std key defined
            self.mean=params["mean"]
            self.std=params["std"]
        elif ("weights" in params):
            self.classes = CLASSES[self.typeDistribution]
            self.weights = params["weights"]
    
    """
    return one value picked randomly based on the parameter type distribution
    """
    def random_choice(self):
        if(self.typeDistribution=="NORMAL"):

            result= list(
                sample_iter(
                    Normal(
                        self.name,
                        self.mean,
                        self.std
                    ),
                    numsamples=1
                )
            )[0]
            return {
                "name":self.name,
                "value":result
            }
        if self.typeDistribution=="LOG":
            result = list(
                sample_iter(
                    LogNormal(
                        self.name,
                        self.mean,
                        self.std
                    ),
                    numsamples=1
                )
            )[0] 
            return {
                "name":self.name,
                "value":result
            }

        ## for LMH or BIN or other types
        result = random.choices(
            self.classes,
            self.weights
        )[0]

        return {
            "name":self.name,
            "value":result
        }


def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""

    # Number of data points: n
    n = len(data)

    # x-data for the ECDF: x
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n

    return x, y

def setup(env,data,sim_params):
    parameters = sim_params["ATA2D"]["ti_parameters"]
    ata2D_aircondition = ATA2D(parameters,sim_params["classes"])
    data["tis"] =[] # collect all tis
    data["mds"] =[] # collect all mainteance demand
    data["ms"]  =[] # collect all maintenance scenarios
    data["iterations"]=[]
    env.process(ata2D_aircondition.run(env,data,sim_params))
    yield env.timeout(1)

def showOccurenceGraph(dataSet):
    x, y = ecdf(dataSet)
    plt.figure(figsize=(8,7))
    sns.set()
    plt.plot(x, y, marker=".", linestyle="none")
    plt.xlabel("Occurence Periodicity (F)")
    plt.ylabel("Cumulative Distribution Function")
    samples = np.random.normal(np.mean(dataSet), np.std(dataSet), size=10000)
    x_theor,y_theor=ecdf(samples)
    plt.plot(x_theor, y_theor)
    plt.legend(('Normal Distribution', 'Empirical Data'), loc='lower right')
    plt.show()
def filterByReportPhase(iteration,phase):
    ti= iteration["ti_parameters"]
    for p in ti:
        if p["name"]=="Report-phase":
            return p["value"]==phase
    return False
    
def filterByBPTO(iteration):
    return filterByReportPhase(iteration,"BPTO")
def filterByFLYING(iteration):
    return filterByReportPhase(iteration,"FLYING")
def filterByPLANNEDSTOP(iteration):
    return filterByReportPhase(iteration,"PLANNED STOP")

def computeDurationMd(iterations,target):
    duration=0
    for iteration in iterations:
        for m in iteration["md_parameters"]:
            duration+= iteration["md_parameters"][m][1]["value"]
    print(f'Maintenance duration where Report phase={target} | duration={round(duration,2)}')
def computeMSFrequences(iterations,ms_dict):
    for it in iterations:
        #print(it["ti_parameters"][1])
        ms_dict[it["scenario"]["scenario"]] += 1
    size=len(iterations)
    print(f'{size}, {ms_dict}')
    return [round((count/size)*100,2) for count in [ms_dict[key] for key in ms_dict]]
# Graph 1 show how the report phase impact on the accessibility
def showGraph1(iterations,sim_params):

    def report(target,ms_dict,result):
        i=0
        print(f'Maintenance scenario, For Report phase=({target})')
        for ms in ms_dict:
            print(f'ti solved with {ms} {result1[i]} % of the times ({ms_dict[ms]} ti)')
            i+=1
    print(f'{len(iterations)} failures')
    bpto_iterations = list(filter(filterByBPTO,iterations))
    flying_iterations = list(filter(filterByFLYING,iterations))
    plannedStop_iterations = list(filter(filterByPLANNEDSTOP,iterations))
    #print(f'{len(bpto_iterations)} BPTO iterations')
    #print(f'{len(flying_iterations)} FLYING iterations')
    #print(f'{len(plannedStop_iterations)} PLANNED_STOP iterations')
    ms_dict1 ={}
    ms_dict2 ={}
    ms_dict3 ={}
    for ms in sim_params["MS"]:
        ms_dict1[ms]=0 
        ms_dict2[ms]=0 
        ms_dict3[ms]=0 
    result1=computeMSFrequences(bpto_iterations,ms_dict1)
    result2=computeMSFrequences(flying_iterations,ms_dict2)
    result3=computeMSFrequences(plannedStop_iterations,ms_dict3)
    report('BPTO',ms_dict1,result1)
    report('FLYING',ms_dict2,result2)
    report('PLANNED STOP',ms_dict3,result3)
    computeDurationMd(bpto_iterations,"BPTO")
    computeDurationMd(flying_iterations,"FLYING")
    computeDurationMd(plannedStop_iterations,"PLANNED")
    computeDurationMd(iterations,"ALL")
    showHisto(bpto_iterations,"BPTO")
    showHisto(flying_iterations,"FLYING")
    showHisto(iterations,"ALL")


def showHisto(iterations,name,intervalNumber=20):
    def convertTwoDigit(value):
        return round(value,2)
    def countValue(sortedList,start,end):
        count = 0
        for value in sortedList:
            if value >= start and value <= end:
                count+=1
            elif value >= end:
                break;
        return count
    def histo(data,indexes):
        n, bins, patches = plt.hist(x=data, bins=indexes, color='#0504aa',
                            )
        plt.grid(axis='y')
        plt.xlabel('Maintenance duration')
        plt.ylabel('Frequency')
        plt.title(f'Maintenance duration for {name}')
        plt.show()
    mds_dict=iterations[0]["md_parameters"]
    durations=[]
    for iteration in iterations:
        for md in iteration["md_parameters"]:
            duration=iteration["md_parameters"][md][1]["value"]
            durations.append(duration)
    durationSorted = list(map(convertTwoDigit,durations))
    durationSorted.sort()
    maxDuration = round(max(durationSorted))
    minDuration= round(min(durationSorted))
    lengthInterval = round((maxDuration-minDuration)/intervalNumber)
    print(f'maxDuration={maxDuration},minDuration={minDuration},length={lengthInterval}')
    indexes=[startInterval for startInterval in range(minDuration,maxDuration,lengthInterval)]
    i=0

    y=[]
    for i in range(len(indexes)-1):
        y.append(countValue(durationSorted,indexes[i],indexes[i+1]))
    print(y)
    print(indexes)
    print(maxDuration,minDuration)
    histo(durationSorted,indexes)

def show_stats(data,sim_params):

    indexTis = [i for i in range(1,len(data["tis"])+1)]
    periodicityList=[]
    for ti in data["tis"]:
        for p in ti:
            if(p["name"]=="Periodicity"):
                periodicityList.append(p["value"])
                break
    #showOccurenceGraph(periodicityList)
    
    showGraph1(data["iterations"],sim_params)
    #print(indexTis)
    #print(data["tis"][0])
    #print(periodicityList)

    
def main():
    data={}
    f = open("parameters.json")
    sim_params = json.load(f)
    env = simpy.Environment()
    env.process(setup(env,data,sim_params))
    env.run(until=sim_params["sim_time"])
    show_stats(data,sim_params)


if __name__=="__main__":
    main()