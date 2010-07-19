import sys

#ModuleFinder can't handle runtime changes to __path__, but win32com uses them
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

from distutils.core import setup
import py2exe  
import shutil

if len(sys.argv) == 1:
    sys.argv.append("py2exe")

# Remove the build tree ALWAYS do that! 
shutil.rmtree("build", ignore_errors=True) 

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the version info resources (Properties -- Version)
        self.version = "0.5.0"
        self.company_name = "my company"
        self.copyright = "? 2006, my company"
        self.name = "my com server name"

my_com_server_target = Target(
    description = "my com server",
    # use module name for win32com exe/dll server
    modules = ["EasyCmdShell"],
    # specify which type of com server you want (exe and/or dll)
    create_exe = True,
    create_dll = False
    )

includes = ["encodings", "encodings.*", "win32com.server"] # "win32com.gen_py.*"] 

setup(
    name="my_com_server",
    # the following two parameters embed support files within exe/dll file
    options={"py2exe": {"bundle_files" : 1, "includes" : includes}},
    zipfile=None,
    version="0.5.0",
    description="my com server",
    # author, maintainer, contact go here:
    author="First Last",
    author_email="some_name@some_company.com",
    com_server=[my_com_server_target]
    )
