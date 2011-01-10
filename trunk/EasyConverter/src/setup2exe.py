from distutils.core import setup 
import glob  
import py2exe 
import sys

if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    
includes = ["encodings", "encodings.*"]  
options = {"py2exe":  
             {   "compressed": 1,  
                 "optimize": 2,  
                 "includes": includes,  
		 "dist_dir": "Friends", 
                 #"bundle_files": 1  
             }  
           }  
setup(     
     version = "0.2.0",  
     description = "Friends Application",  
     name = "Friends",  
     options = options,  
     zipfile=None,  
     windows=[{"script": "Friends.py", "icon_resources": [(1, "Friends.ico")] }],    
     data_files=[("", ["friends.cfg", 'Friends.ico', 'app\\FileTransfer.py']), ("res",glob.glob("res\\*.png"))],  
     ) 