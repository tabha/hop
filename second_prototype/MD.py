from Parameter import Parameter

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
