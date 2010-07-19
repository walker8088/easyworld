import sys, os
import wx
import drPrefsFile
from drPreferences import drPreferences

import glob, utils

global app
global prefs, prefsfile, preferencesdirectory, programdirectory
global PLATFORM_IS_WIN, PLATFORM_IS_GTK, PLATFORM_IS_MAC
global pythexec, pythexecw

prefdialogposition = 0

#*******************************************************************************************************
logdir = os.path.expanduser("~").replace("\\", "/")
if sys.platform == "win32":
    if os.environ.has_key("APPDATA"):
        logdir = os.environ["APPDATA"].replace("\\", "/")
    if not os.path.exists(logdir):
        logdir = '/'
if not logdir.endswith('/'):
    logdir += '/'
        
#*******************************************************************************************************
def Init() :   
        global app
        global prefs, prefsfile, preferencesdirectory, programdirectory
        global PLATFORM_IS_WIN, PLATFORM_IS_GTK, PLATFORM_IS_MAC
        global pythexec, pythexecw
        
        app = wx.GetApp()
        
        #System constants
        PLATFORM_IS_WIN = wx.Platform == '__WXMSW__' # (sys.platform == "win32") or #wx.PLATFORM_WINDOWS or wx.PLATFORM_WINDOWS
        PLATFORM_IS_GTK = wx.Platform == '__WXGTK__'
        PLATFORM_IS_MAC = wx.Platform == '__WXMAC__'
        
        if PLATFORM_IS_WIN:
            pythexec = sys.prefix.replace("\\", "/") + "/python.exe"
            pythexecw = sys.prefix.replace("\\", "/") + "/pythonw.exe"
        else:
            pythexec = sys.executable

        #Preferences
        preferencesdirectory = ""
        programdirectory = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    
        prefs = drPreferences(PLATFORM_IS_WIN, programdirectory)
        prefsfile = preferencesdirectory + "/preferences.dat"

        LoadPreferences()
        SetEasyPythonDirectories()
        
        utils.Init()
        
        if prefs.defaultdirectory:
            glob.CurrDir = prefs.defaultdirectory
        else:
            #add limodou 2004/04/17
            #if defaultdirectory is empty, then use the last recently file's dir
            if glob.recentfiles:
                glob.CurrDir = os.path.dirname(glob.recentfiles[0])
            #end limodou
            else:
                glob.CurrDir = programdirectory

        try:
            os.chdir(glob.CurrDir)
        except:
            glob.CurrDir = programdirectory
            os.chdir(glob.CurrDir)

    
#*******************************************************************************************************
def LoadPreferences():
        global app
        global prefs, prefsfile, preferencesdirectory, programdirectory
        global PLATFORM_IS_WIN, PLATFORM_IS_GTK, PLATFORM_IS_MAC
        global pythexec, pythexecw

        #check for preferences file in user userpreferencesdirectory
        if os.path.exists(prefsfile):
            try:
                drPrefsFile.ReadPreferences(prefs, prefsfile)
            except:
                self.ShowMessage(("Error with: " + prefsfile + "\nEasyPython will load the program defaults."), "Preferences Error")
                prefs.reset()
                drPrefsFile.WritePreferences(prefs, prefsfile)
        else:
            drPrefsFile.WritePreferences(prefs, prefsfile)
        wx.GetApp().debugmodus = prefs.debugmodus
        # already restted
        if prefs.defaultencoding:
            reload(sys)  #this is needed because of wine and linux
            sys.setdefaultencoding(prefs.defaultencoding)
            wx.SetDefaultPyEncoding(prefs.defaultencoding)

#*******************************************************************************************************
global BitmapDir, datdirectory, shortcutsdirectory 
def SetEasyPythonDirectories():
        global BitmapDir, datdirectory, shortcutsdirectory 
        #bitmaps code directory
        BitmapDir = programdirectory + "/bitmaps"
        if not os.path.exists(BitmapDir):
            utils.ShowMessage("Bitmap Directory (" + BitmapDir + ") does Not Exist.", "EasyPython Fatal Error")
            sys.exit(1)

        #dat directory
        datdirectory = os.path.join(preferencesdirectory, 'dat')
        if not os.path.exists(datdirectory):
            os.mkdir(datdirectory)

        #shortcuts directory
        shortcutsdirectory = os.path.join(preferencesdirectory, 'shortcuts')
        if not os.path.exists(shortcutsdirectory):
            os.mkdir(shortcutsdirectory)

def WriteUserPreferencesDirectoryFile():
        f = open(preferencesdirectoryfile, 'w')
        f.write(preferencesdirectory)
        f.close()


#*******************************************************************************************************
            