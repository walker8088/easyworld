
import os, re
import wx
import config 

app = None
mainFrame = None
docMgr = None

PYTHON_FILE, HTML_FILE, TEXT_FILE = range(3)

IgnoreEvents = False
DisableEventHandling = False

LastProgArgs = ""
                
CurrDir = ""
       
FindHistory = []
ReplaceHistory = []
FindInFilesHistory = []
ReplaceInFilesHistory = []
FindOptions = []
ReplaceOptions = []

RecentFiles = []
        
FormatMacReTarget = re.compile('((?<!\r)\n)|(\r\n)', re.M)
FormatUnixReTarget = re.compile('(\r\n)|(\r(?!\n))', re.M)
FormatWinReTarget = re.compile('((?<!\r)\n)|(\r(?!\n))', re.M)

PopupMenuList = []

#**********************************************************************************    
def LoadRecentFiles():
        f = config.AppDataDir + "/recent_files.log"
        if not os.path.exists(f):
            try:
                t = open(f, 'w')
                t.close()
            except IOError:
                if config.prefs.debugmodus:
                    utils.ShowMessage("Error Creating: " + f + "\nMaybe you don't have right access or harddisk is full" , "Recent Files Error")
                    utils.AskExitingEasyPython()

        try:
            fin = open(f, 'r')
            s = fin.readline()
            x = 0
            while (len(s) > 0) and (x < config.prefs.recentfileslimit):
                s = s.rstrip()
                if s:
                    RecentFiles.append(s)
                x = x + 1
                s = fin.readline()
            fin.close()
        except IOError:
            utils.ShowMessage(("Error Reading: " + f), "Recent Files Error")
            utils.AskExitingEasyPython()
    
def WriteRecentFiles():
        recentfiles = config.AppDataDir + "/recent_files.log"
        try:
            fin = open(recentfiles, 'w')
            x = 0
            length = len(RecentFiles)
            while (x < config.prefs.recentfileslimit) and (x < length):
                fin.write(RecentFiles[x] + '\n')
                x = x + 1
            fin.close()
        except IOError:
            utils.ShowMessage("Error Writing: " + recentfiles, "Recent Files Error")

#**********************************************************************************
def getIcon(self, bitmap):
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(bitmap)
    return icon

defImages = {}

def getBitmap(name):
    if name not in defImages.keys() :
        defImages[name] = wx.Image(os.path.join('bitmaps', '24', name + '.png'), wx.BITMAP_TYPE_PNG)   
        #print name
    return wx.BitmapFromImage(defImages[name])
#**********************************************************************************
    
            