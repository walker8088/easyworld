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
                 "dist_dir": "bin", 
                 "bundle_files": 1  
             }  
           }  
setup(     
     version = "1.0",  
     description = "EasyPython Application",  
     name = "EasyPython",  
     options = options,  
     zipfile=None,  
     windows=[{"script": "EasyPython.py", "icon_resources": [(1, "EasyPython.ico")] }],    
     data_files=[("",['EasyPython.ico']),
                 ("data",glob.glob("data\\*.dat")),
                 ("documentation",glob.glob("documentation\\*.*")),
                 ("bitmaps",glob.glob("bitmaps\\*.*")),
                 ("bitmaps\\24",glob.glob("bitmaps\\24\\*.*")),
                 ("bitmaps\\16",glob.glob("bitmaps\\16\\*.*")),
                 
                 ],  
     ) 