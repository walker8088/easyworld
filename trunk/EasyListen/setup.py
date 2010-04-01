
import sys
from distutils.core import setup  
import py2exe  

if len(sys.argv) == 1:
    sys.argv.append("py2exe")

includes = ["encodings", "encodings.*"]  
options = {"py2exe":  
             {   "compressed": 1,  
                 "optimize": 2,  
                 "includes": includes,  
                 "bundle_files": 1  
             }  
           }  
setup(     
     version = "0.1.0",  
     description = "Easy Listen Application",  
     name = "easylisten",  
     options = options,  
     zipfile=None,  
     windows=[{"script": "easylisten.pyw", "icon_resources": [(1, "easylisten.ico")] }],    
     data_files=[("", ["easylisten.ico"]) ]  
     )  
