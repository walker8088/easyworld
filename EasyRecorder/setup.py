
import os, sys, shutil
from distutils.core import setup
import py2exe

if len(sys.argv) == 1:
    sys.argv.append("py2exe")

APP_NAME = 'EasyRecorder'
RT_MANIFEST = 24

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

manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''


includes = ["encodings", "encodings.*"]  

options = {"py2exe":  
             {   "compressed": 1,  
                 "optimize": 2,  
                 "dist_dir": ".", 
                 "includes": includes,
                 "bundle_files": 1  
             }  
           }  
setup(     
     version = "1.0",  
     description = APP_NAME,  
     name = APP_NAME,  
     options = options,  
     zipfile = None,  
     windows=[{"script": APP_NAME + ".pyw", 
                "icon_resources": [(1, APP_NAME + ".ico"), (2, "record.ico"), (3, "stop.ico")], 
                "other_resources":[(RT_MANIFEST, 1, manifest_template % dict(prog=APP_NAME))],               
                }],    
     ) 

os.remove("w9xpopen.exe")     
os.remove("msvcr71.dll")     
shutil.rmtree("build")
     