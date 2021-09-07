import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


"""
This function is a helper, to verify the distribution type of a dataset
it sort the array an generate a list of index from 1 to the length dataset + 1
"""

def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    n = len(data)
    # x-data for the ECDF: x
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n

    return x, y

"""
this function helped to validate the behavior of the occurence periodicity,
in the input parameters, we defined it as a normal distribution
"""
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


def filterByBPTO(iteration):
    return filterByParameter(iteration,"Report-phase","BPTO")
def filterByFLYING(iteration):
    return filterByParameter(iteration,"Report-phase","FLYING")
def filterByPLANNEDSTOP(iteration):
    return filterByParameter(iteration,"Report-phase","PLANNED STOP")

def filterByParameter(iteration,nameParameter,targetValue):
    ti = iteration["ti_parameters"]
    for p in ti:
        if p["name"]==nameParameter:
            return p["value"]==targetValue
    return False
def filterByImpactScore(iteration,state):
    return iteration["scenario"]["impact"] == state

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

"""
show histogram graphs for all types of report phase
BPTO
FLYING
PLANNED_STOP
ALL of them
"""
def showMdDurationGraphs(iterations,sim_params):

    def report(target,ms_dict,result):
        i=0
        print(f'Maintenance scenario, For Report phase=({target})')
        for ms in ms_dict:
            print(f'ti solved with {ms} {result[i]} % of the times ({ms_dict[ms]} ti)')
            i+=1
    print(f'{len(iterations)} failures')
    bpto_iterations = list(filter(filterByBPTO,iterations))
    flying_iterations = list(filter(filterByFLYING,iterations))
    plannedStop_iterations = list(filter(filterByPLANNEDSTOP,iterations))

    print(f'{len(bpto_iterations)} BPTO iterations')
    print(f'{len(flying_iterations)} FLYING iterations')
    print(f'{len(plannedStop_iterations)} PLANNED_STOP iterations')
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
    
    fig, axs = plt.subplots(2,2,figsize=(12,10))
    bptoAxis=axs[0,0]
    flyingAxis=axs[0,1]
    planedAxis=axs[1,0]
    allAxis=axs[1,1]
    showHistoMdDuration(bpto_iterations,"BPTO",bptoAxis)
    showHistoMdDuration(flying_iterations,"FLYING",flyingAxis)
    showHistoMdDuration(plannedStop_iterations,"PLANNED STOP",planedAxis)
    showHistoMdDuration(iterations,"ALL",allAxis)
    plt.show()
"""
draw a histogram in the axis,
intervalNumber helps to regroup values
let say we have a list of maintenance duration, we want to draw a histogram
first we will sort the list an regroup value in intervals
so that we can count the frequency of values within an interval

"""
def showHistoMdDuration(
        iterations,
        name,
        axis,
        intervalNumber=20,
    ):
    """
    round value to two digit format
    """
    def convertTwoDigit(value):
        return round(value,2)
    def countValue(sortedList,start,end):
        count = 0
        for value in sortedList:
            if value >= start and value < end:
                count+=1
            elif value >= end:
                break;
        return count
    def histo(data,indexes,axis):
        axis.hist(x=data, bins=indexes, color='#0504aa')
        axis.grid(axis='y')
        axis.set_title(f'Maintenance duration for {name}')
        axis.set(xlabel="Maintenance duration",ylabel="Frequency")
        
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
    histo(durationSorted,indexes,axis)


def showDistributionMS(iterations,state,ms_list):
    print(ms_list)
    print(f'{len(iterations)} tis with {state} impact')
    for ms in ms_list:
        print(f'------ti solved with {ms} {(round(countValuesForMS(iterations,ms)/len(iterations)*100,2))} %')

def countValuesForMS(iterations,ms):
    #first filter by ms
    def filterbyMs(iteration):
        return iteration["scenario"]["scenario"] == ms
    ms_tis = list(filter(filterbyMs,iterations))
    return len(ms_tis)
def showMSFrequenciesBasedOnReportPhase(iterations,ms_list):
    
    def filterByHighState(iteration):
        return filterByImpactScore(iteration,"HIGH")
    def filterByMediumState(iteration):
        return filterByImpactScore(iteration,"MEDIUM")
    def filterByLowState(iteration):
        return filterByImpactScore(iteration,"LOW")
    
    tisWithHighImpact = list(filter(filterByHighState,iterations))
    tisWithMediumImpact = list(filter(filterByMediumState,iterations))
    tisWithLowImpact = list(filter(filterByLowState,iterations))
    print(f'tis with impact score ="HIGH", {len(tisWithHighImpact)} tis')    
    print(f'tis with impact score ="MEDIUM", {len(tisWithMediumImpact)} tis')    
    print(f'tis with impact score ="LOW", {len(tisWithLowImpact)} tis') 
    showDistributionMS(tisWithHighImpact,"HIGH",ms_list)  
    showDistributionMS(tisWithMediumImpact,"MEDIUM",ms_list)  
    showDistributionMS(tisWithLowImpact,"LOW",ms_list)  
def show_stats(data,sim_params):

    indexTis = [i for i in range(1,len(data["tis"])+1)]
    periodicityList=[]
    for ti in data["tis"]:
        for p in ti:
            if(p["name"]=="Periodicity"):
                periodicityList.append(p["value"])
                break
    #showOccurenceGraph(periodicityList)
    ms_list=[ms for ms in sim_params["MS"]]
    showMdDurationGraphs(data["iterations"],sim_params)
    showMSFrequenciesBasedOnReportPhase(data["iterations"],ms_list)
    #print(indexTis)
    #print(data["tis"][0])
    #print(periodicityList)
