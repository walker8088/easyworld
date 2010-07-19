import sys

from distutils.core import setup  
import py2exe  

if len(sys.argv) == 1:
    sys.argv.append("py2exe")

includes = ["encodings", "encodings.*",]  
options = {"py2exe":  
             {   "compressed": 1,  
                 "optimize": 2,  
                 "includes": includes,  
                 "bundle_files": 1  
             }  
           }  
setup(     
     version = "1.0",  
     name = "CodeReport",  
     options = options,  
     zipfile=None,  
     console=[{"script": "CodeReport.py", }]  
     )  
