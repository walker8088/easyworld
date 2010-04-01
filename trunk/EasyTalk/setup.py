
from distutils.core import setup  
import py2exe  
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
     description = "Easy Talk Application",  
     name = "EasyTalk",  
     options = options,  
     zipfile=None,  
     windows=[{"script": "easytalk.py", "icon_resources": [(1, "easytalk.ico")] }],    
     data_files=[("", ["ring.wav", "ringback.wav","easytalk.ico"]) ]  
     )  
