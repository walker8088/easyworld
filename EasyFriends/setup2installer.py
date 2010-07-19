# A setup script showing how to extend py2exe.
#
# In this case, the py2exe command is subclassed to create an installation
# script for InnoSetup, which can be compiled with the InnoSetup compiler
# to a single file windows installer.
#
# By default, the installer will be created as dist\Output\setup.exe.

from distutils.core import setup
import py2exe
import sys,os
import ctypes
import glob

from py2exe.build_exe import py2exe

if len(sys.argv) == 1:
    sys.argv.append("py2exe")

# ###############################################################
APP_NAME        = 'Friends'
APP_ICON_FILE   = 'Friends.ico'
APP_CONFIG_FILE = 'Friends.cfg'
APP_SCRIPT_FILE = 'Friends.py'
APP_VERSION     = '0.20'
# ###############################################################

# The manifest will be inserted as resource into NewEraEngine.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store if in a file named
# NewEraEngine.exe.manifest, and probably copy it with the data_files
# option.
#
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

RT_MANIFEST = 24

# ###############################################################
class InnoScript:
    def __init__(self, name, version, lib_dir, dist_dir, windows_exe_files, lib_files):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = lib_files #[self.chop(p) for p in lib_files]
       

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]
    
    def create(self, pathname):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        #wirte tscripy here
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.windows_exe_files + self.lib_files:
           if os.path.basename(path) in ['w9xpopen.exe', 'python25.dll']:
               continue
           print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, '')
        print >> ofi

        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"; WorkingDir: "{app}"' % \
                  (self.name, path)
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"; WorkingDir: "{app}"' % self.name

    def compile(self):
        res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                                                      self.pathname,
                                                      None,
                                                      None,
                                                      0)
        if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res

# ###############################################################
class build_installer(py2exe):
    # This class first builds the exe file(s), then creates a Windows installer.
    # You need InnoSetup for it.
    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)
        
        # create the Installer, using the files py2exe has created.
        script = InnoScript(APP_NAME,
                            APP_VERSION,
                            self.lib_dir,
                            self.dist_dir,
                            self.windows_exe_files,
                            self.lib_files,
                            )
        print "*** creating the inno setup script***"
        script.create("dist\\" + APP_NAME + ".iss")
        print "*** compiling the inno setup script***"
        script.compile()
        print "OK! By default the final setup.exe will be in an Output subdirectory."

# ###############################################################

options = {"py2exe": 
                {
                "compressed": 1, 
                "optimize": 2, 
                #"bundle_files": 1
                }
          }

setup(
    options = options,
    zipfile = None,
    windows = [{
                "script":APP_SCRIPT_FILE, 
                "icon_resources": [(1, APP_ICON_FILE)]
              }],
    cmdclass = {"py2exe": build_installer},
    data_files = [
                ("",glob.glob(APP_ICON_FILE)),
                ("",glob.glob(APP_CONFIG_FILE)), 
                #("",glob.glob("msvcp71.dll"))
                ],
    #other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="EIOCenter"))],            
    )
