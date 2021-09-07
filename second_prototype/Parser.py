import os
import json

MD_SPEC_="md_spec.json"
class ParameterParser(object):

    def __init__(self,dirpath):
        self.dirpath = dirpath
    def parse(self):
        for subdir, dirs, files in os.walk(self.dirpath):
            for ata2dSpec in dirs:
                ata2dSpec_md_spec = subdir + os.sep + ata2dSpec +  os.sep + MD_SPEC_
                try:
                    with open(ata2dSpec_md_spec) as spec_json:                    
                        spec = json.load(spec_json)
                        print(spec)
                except:
                    None
            