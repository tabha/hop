
from MD import MaintenanceDemand
from Parameter import Parameter
import random

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
        score = (
                    (sim_params["aw_impact_weight"]*aw_score)+
                    (sim_params["perf_impact_weight"]*perf_score)+
                    (sim_params["report_impact_weight"]*report_phase_score)
                )
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
