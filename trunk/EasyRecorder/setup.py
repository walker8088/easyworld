import sys

if len(sys.argv) == 1:
    sys.argv.append("py2exe")

#Fix  win32com problem for py2exe     
try:
    # if this doesn't work, try import modulefinder
    import py2exe.mf as modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
        for extra in ["win32com.shell"]: #,"win32com.mapi"
           __import__(extra)
           m = sys.modules[extra]
           for p in m.__path__[1:]:
               modulefinder.AddPackagePath(extra, p)
except ImportError:
       # no build path setup, no worries.
      pass
#end Fix

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
     description = "Easy Recorder For Windows",  
     name = "EasyRecorder",  
     options = options,  
     zipfile=None,  
     windows=[{"script": "EasyRecorder.py", "icon_resources": [(1, "EasyRecorder.ico"), (2, "record.ico"), (3, "stop.ico")] }],    
     #data_files=[("icons", ["icons\\record.ico", "icons\\stop.ico"]) ]  
     )  
