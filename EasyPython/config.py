import sys, os
import wx
import drPrefsFile
from drPreferences import drPreferences

import glob, utils

global app
global prefs, prefsfile, AppDataDir, AppDir,BitmapDir
global BitmapDir, AppDataDir, AppDataDir 
global PLATFORM_IS_WIN, PLATFORM_IS_GTK, PLATFORM_IS_MAC
global pythexec, pythexecw

prefdialogposition = 0
        
#*******************************************************************************************************
def Init() :   
        global app
        global prefs, prefsfile, AppDataDir, AppDir,BitmapDir
        global PLATFORM_IS_WIN, PLATFORM_IS_GTK, PLATFORM_IS_MAC
        global pythexec, pythexecw
        
        app = wx.GetApp()
        
        #System constants
        PLATFORM_IS_WIN = wx.Platform == '__WXMSW__' # (sys.platform == "win32") or #wx.PLATFORM_WINDOWS or wx.PLATFORM_WINDOWS
        PLATFORM_IS_GTK = wx.Platform == '__WXGTK__'
        PLATFORM_IS_MAC = wx.Platform == '__WXMAC__'
        
        if PLATFORM_IS_WIN:
            pythexec = sys.prefix.replace("\\", "/") + "/python.exe"
            pythexecw = sys.prefix.replace("\\", "/") + "/python.exe"
        else:
            pythexec = sys.executable

        #Preferences
        AppDir = utils.module_path()
        AppDataDir = os.path.join(AppDir,"data")
        if not os.path.exists(AppDataDir):
            os.mkdir(AppDataDir)

        BitmapDir = os.path.join(AppDir,"bitmaps")
        if not os.path.exists(BitmapDir):
            utils.ShowMessage("Bitmap Directory (" + BitmapDir + ") does Not Exist.", "EasyPython Fatal Error")
            sys.exit(1)
        
        prefsfile = os.path.join(AppDataDir,"preferences.dat")
      
        prefs = drPreferences(PLATFORM_IS_WIN, AppDir)
        
        LoadPreferences()
        
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
                glob.CurrDir = AppDir

        try:
            os.chdir(glob.CurrDir)
        except:
            glob.CurrDir = AppDir
            os.chdir(glob.CurrDir)

    
#*******************************************************************************************************
def LoadPreferences():
        global app
        global prefs, prefsfile, AppDataDir, AppDir
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