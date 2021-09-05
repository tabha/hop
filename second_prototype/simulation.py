import simpy
import random
import json
from ATA2D import ATA2D
from Stats import show_stats
class Simulation:
    def __init__(self,inputJson_path="parameters.json"):
        f = open("parameters.json") # to be replaced by a class that handle parsing input json files
        self.sim_params = json.load(f)  # same
        self.env = simpy.Environment()  # initializing the simpy environement
        self.data = {}                  # create a dictionnary that hold everything the initialization is done in setup function
    """
    This function is the starting point of the simulation
    where we get ready the environement
    initialize the ATA2D we are simulation, by passing the input parameter
    the data collecter is initalized so that later we can do data analysis.
    """
    def setup(self):
        parameters = self.sim_params["ATA2D"]["ti_parameters"]
        ata2D_aircondition = ATA2D(parameters,self.sim_params["classes"]) # create an instance of an ATA2D
        
        self.data["tis"] =[] # collect all tis
        self.data["mds"] =[] # collect all mainteance demand
        self.data["ms"]  =[] # collect all maintenance scenarios
        self.data["iterations"]=[]
        self.env.process(ata2D_aircondition.run(self.env,self.data,self.sim_params)) # start the simulation here
        yield self.env.timeout(1)                                          # to keep the environement a live until all simulation is done
    """
    This is the main function that run de simulation
    """
    def run(self):
        self.env.process(self.setup())# run the first function
        self.env.run(until=self.sim_params["sim_time"])
        show_stats(self.data,self.sim_params)
    
def main():
    simulation=Simulation()
    simulation.run()
if __name__=="__main__":
    main()