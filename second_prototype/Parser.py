import os
import json

MD_SPEC_DIR="mds"
class ParameterParser(object):

    def __init__(self,dirpath):
        self.dirpath = dirpath
        self.result = {}
    
    def mergeMD(self,path):
        
        with open(path) as spec_json:                    
            spec = json.load(spec_json)
            self.result["MD"][spec["alias"]]={}
            for s in spec:
                self.result["MD"][spec["alias"]][s]=spec[s]
        
    def mergeMS(self,path):
        with open(path) as spec_json:                    
            spec = json.load(spec_json)
            for s in spec:
                self.result[s]=spec[s]


    def parse(self):
        self.result["MS"]={}
        self.result["MD"]={}
        for subdir, dirs, files in os.walk(self.dirpath):
            for direct in dirs:
                mds_dir = subdir + os.sep + direct 
                for subdir1,dirs2,files2 in os.walk(mds_dir):
                    for file in files2:
                        path = subdir1 + os.sep + file
                        if file.startswith("md") and file.endswith(".json"):
                            self.mergeMD(path)
                        elif file.endswith(".json"):
                            self.mergeMS(path) 

        return self.result