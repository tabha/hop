"""
This class will handle how a paremeter is simulated

"""
from sympy.stats import Normal, sample_iter, LogNormal
import random

class Parameter:

    """
    Supported typeDistribution are
    LMH for Low medium high
    BIN for Binary distribution only two classes 
    NORMAL for parameter that folows normal distributions
    LOG for parameters that follows Log normal distributions
    mean and std are only used for Normal and LOG typesDistributions
    """
    def __init__(self,params,classes):
        self.name = params["name"]
        self.typeDistribution = params["type"]
        if ("mean" in params) and ("std" in params):
            # only Log and log Noraml parameters has mean and std key defined
            self.mean=params["mean"]
            self.std=params["std"]
        elif ("weights" in params):
            self.classes = classes[self.typeDistribution]
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

