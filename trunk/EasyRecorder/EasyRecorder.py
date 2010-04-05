
from win32api import *
try:
    from winxpgui import *
except ImportError:
    from win32gui import *
from win32gui_struct import *
import win32con
import sys, os, os.path
import struct
import array
from datetime import datetime

from recordwin32 import Recorder

from win32com.shell import shell

def GetHomeDir() :
    df = shell.SHGetDesktopFolder()
    pidl = df.ParseDisplayName(0, None,  "::{450d8fba-ad25-11d0-98a8-0800361b1103}")[1]
    mydocs = shell.SHGetPathFromIDList(pidl)
    return mydocs
    
class MainWindow:
    ID_EXIT  = 1000
    ID_START = 1001
    ID_STOP  = 1002
    ID_CONFIG= 1003
    
    def __init__(self):
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_COMMAND: self.OnCommand,
                win32con.WM_USER+20 : self.OnTaskbarNotify,
        }
        
        # Register the Window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "EasyRecorder"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = RegisterClass(wc)
        
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow( classAtom, "EasyRecorder", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, hinst, None)
        UpdateWindow(self.hwnd)
        
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        
        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe":
                self.record_icon = CreateIconFromResource(LoadResource(None, win32con.RT_ICON, 1), True)
                self.stop_icon = CreateIconFromResource(LoadResource(None, win32con.RT_ICON, 2), True)
        else :
                self.record_icon = LoadImage(hinst, "record.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
                self.stop_icon = LoadImage(hinst, "stop.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
        
        self.workdir = GetHomeDir()
        self.recorder = Recorder(samplesize=16, samplerate=8192, channels=1)  
        
        self.createMenu()        
        
        nid = (self.hwnd, 0, NIF_ICON | NIF_MESSAGE | NIF_TIP, win32con.WM_USER+20, self.record_icon, "Easy Recorder")
        Shell_NotifyIcon(NIM_ADD, nid)
        
        EnableMenuItem(self.hmenu, self.ID_START, win32con.MF_BYCOMMAND|win32con.MF_ENABLED)
        EnableMenuItem(self.hmenu, self.ID_STOP, win32con.MF_BYCOMMAND|win32con.MF_DISABLED|win32con.MF_GRAYED)
        SetMenuDefaultItem(self.hmenu, self.ID_START, 0)
        
    def createMenu(self):
        self.hmenu = menu = CreatePopupMenu()
        
        item, extras = PackMENUITEMINFO(text = "Exit", wID = self.ID_EXIT)
        InsertMenuItem(menu, 0, 1, item)
        
        item, extras = PackMENUITEMINFO(text="Stop", wID = self.ID_STOP)
        InsertMenuItem(menu, 0, 1, item)
        
        item, extras = PackMENUITEMINFO(text = "Start", wID = self.ID_START)
        InsertMenuItem(menu, 0, 1, item)
        
        #item, extras = PackMENUITEMINFO(text = "Config", wID = self.ID_CONFIG)
        #InsertMenuItem(menu, 0, 1, item)
        
        SetMenuDefaultItem(menu, self.ID_START, 0)
 
    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0) # Terminate the app.

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_RBUTTONUP:
            pos = GetCursorPos()
            SetForegroundWindow(self.hwnd)
            TrackPopupMenu(self.hmenu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        elif lparam==win32con.WM_LBUTTONDBLCLK:
            cmd = GetMenuDefaultItem(self.hmenu, False, 0)
            if cmd != -1:
                self.OnCommand(hwnd, win32con.WM_COMMAND, cmd, 0)
        return 1
    
    def StartRecord(self) :        
        fileName = os.path.join(self.workdir, "record_" + datetime.now().strftime('%Y%m%d-%H%M%S') +'.wav')
        try :
            self.recorder.start(fileName)
        except :
            pass
        
        EnableMenuItem(self.hmenu, self.ID_START, win32con.MF_BYCOMMAND|win32con.MF_DISABLED|win32con.MF_GRAYED)
        EnableMenuItem(self.hmenu, self.ID_STOP, win32con.MF_BYCOMMAND|win32con.MF_ENABLED)
        
        SetMenuDefaultItem(self.hmenu, self.ID_STOP, 0)
        
        nid = (self.hwnd, 0, NIF_ICON | NIF_MESSAGE | NIF_TIP, win32con.WM_USER+20, self.stop_icon, "Easy Recorder")
        Shell_NotifyIcon(NIM_MODIFY, nid)
         
    def StopRecord(self) :
        self.recorder.stop()
        EnableMenuItem(self.hmenu, self.ID_START, win32con.MF_BYCOMMAND|win32con.MF_ENABLED)
        EnableMenuItem(self.hmenu, self.ID_STOP, win32con.MF_BYCOMMAND|win32con.MF_DISABLED|win32con.MF_GRAYED)
        SetMenuDefaultItem(self.hmenu, self.ID_START, 0)
        
        nid = (self.hwnd, 0, NIF_ICON | NIF_MESSAGE | NIF_TIP, win32con.WM_USER+20, self.record_icon, "Easy Recorder")
        Shell_NotifyIcon(NIM_MODIFY, nid)
        
    def OnCommand(self, hwnd, msg, wparam, lparam):
        id = LOWORD(wparam)
        if id == self.ID_START :
            self.StartRecord()
        elif id == self.ID_STOP :
            self.StopRecord()
        elif id == self.ID_CONFIG :
            pass
        elif id == self.ID_EXIT :
            self.StopRecord()
            DestroyWindow(self.hwnd)
            
def main():
    w=MainWindow()
    PumpMessages()

if __name__=='__main__':
    main()
