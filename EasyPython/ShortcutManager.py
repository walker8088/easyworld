
import os

import drShortcutsFile
import drShortcuts

import config, glob

class ShortcutManager :

    def __init__(self) :
        
        self.stcshortcutlist = drShortcutsFile.GetSTCShortcutList()
        
        #Shortcuts
        self.STCShortcuts = drShortcutsFile.GetDefaultSTCShortcuts()
        self.STCShortcutNames = drShortcutsFile.GetSTCShortcutList()
        self.STCShortcutsArgumentArray = drShortcuts.GetSTCCommandList()
        self.Shortcuts, self.ShortcutsIgnoreString = drShortcutsFile.GetDefaultShortcuts()
        self.ShortcutNames = drShortcutsFile.GetShortcutList()
        self.ShortcutsActionArray = []
        self.ShortcutsArgumentsArray = []
        
        #Load Shortcuts

        self.STCUseDefault = 1
        self.ShortcutsUseDefault = 1

        self.LoadShortcuts()

        #Shortcuts
        #drShortcuts.SetSTCShortcuts(self.txtPrompt, self.STCShortcuts, self.STCUseDefault)
        #self.STCShortcuts = drShortcuts.SetSTCShortcuts(self.currDoc, self.STCShortcuts, self.STCUseDefault)
        #self.Shortcuts, self.ShortcutsActionArray, self.ShortcutsArgumentsArray = drShortcuts.SetShortcuts(self, self.Shortcuts, self.ShortcutNames, self.ShortcutsUseDefault)
        
        #STC Shortcut List:
        self.STCCOMMANDLIST = drShortcuts.GetSTCCommandList()
    
    def GetMenuLabel(self, label, LaunchesDialog=False, AmpersandAt=-1, absolutelabel=''):
        shortcuttext = ''

        if label in self.ShortcutNames:
            i = self.ShortcutNames.index(label)
            shortcuttext = drShortcuts.GetShortcutLabel(self.Shortcuts[i])
        elif label in self.STCShortcutNames:
            i = self.STCShortcutNames.index(label)
            shortcuttext = drShortcuts.GetShortcutLabel(self.STCShortcuts[i])

        if absolutelabel:
            label = absolutelabel
        else:
            if (AmpersandAt > -1) and (AmpersandAt < len(label)):
                label = label[:AmpersandAt] + '&' + label[AmpersandAt:]
            if LaunchesDialog:
                label += '...'

        if len(shortcuttext) > 1:
            return label + '\t' + shortcuttext
        return label
    
    def LoadShortcuts(self, UseDefault = False):
        #Load STC Shortcuts
        stcshortcutsfile = config.shortcutsdirectory + "/stcshortcuts.dat"
        if os.path.exists(stcshortcutsfile) and (not UseDefault):
            try:
                self.STCShortcuts, self.STCShortcutNames, t = drShortcutsFile.ReadSTCShortcuts(stcshortcutsfile)
                self.STCUseDefault = 0
            except:
                utils.ShowMessage(("Error with: " + stcshortcutsfile + "\nEasyPython will not load STC shortcuts."),
                                  "STC Shortcuts Error")

        #check for shortcuts file in user userpreferencesdirectory
        shortcutsfile = config.shortcutsdirectory + "/shortcuts.dat"
        if os.path.exists(shortcutsfile) and (not UseDefault):
            try:
                self.Shortcuts, self.ShortcutNames, self.ShortcutsIgnoreString = drShortcutsFile.ReadShortcuts(shortcutsfile)
                self.ShortcutsUseDefault = 0
            except:
                utils.ShowMessage(("Error with: " + shortcutsfile + "\nEasyPython will load the program defaults."),
                                  "Shortcuts Error")
                self.LoadShortcuts(True)

    def AddKeyEvent(self, function, Keycode, Control=0, Shift=0, Alt=0, Meta=0):
        if Keycode == -1:
            return

        shortcut = drShortcuts.BuildShortcutString(Keycode, Control, Shift, Alt, Meta)
    