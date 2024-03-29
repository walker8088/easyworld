#coding: utf8

import os, os.path
import pythoncom
from win32com.shell import shell, shellcon
import win32gui, win32con, win32process, win32event, win32api
from win32com.server import register
import _winreg
   
from LineCounter import *
   
class ShellExtension:
    _reg_progid_ = "ShellExtension.ContextMenu.EasyCLOC"
    _reg_desc_ = "Line Counter Shell Extension"
    _reg_clsid_ = "{CED0336C-C0EF-4a7f-9D7F-C660393C381A}"
    _com_interfaces_ = [shell.IID_IShellExtInit, shell.IID_IContextMenu]
    _public_methods_ = shellcon.IContextMenu_Methods + shellcon.IShellExtInit_Methods
    folder = None
    
    def Initialize(self, folder, dataobj, hkey):
        print "Init", folder, dataobj, hkey
        self.folder = folder
        self.dataobj = dataobj

    def QueryContextMenu(self, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):    
        if (uFlags & 0x000F) != shellcon.CMF_NORMAL: 
                return 0
                
        format_etc = win32con.CF_HDROP, None, 1, -1, pythoncom.TYMED_HGLOBAL
        sm = self.dataobj.GetData(format_etc)
        num_files = shell.DragQueryFile(sm.data_handle, -1)
        if num_files != 1:
                return 0
                
        folder_name = shell.DragQueryFile(sm.data_handle, 0)
        if not os.path.isdir(folder_name) :
                return 0
                
        self.folder = folder_name

        idCmd = idCmdFirst
        win32gui.InsertMenu(hMenu, indexMenu,
                            win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                            0, None)
        indexMenu += 1
        win32gui.InsertMenu(hMenu, indexMenu,
                        win32con.MF_STRING|win32con.MF_BYPOSITION,
                        idCmd, u'统计代码行数')
        indexMenu += 1
        idCmd += 1

        win32gui.InsertMenu(hMenu, indexMenu,
                            win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                            0, None)
        indexMenu += 1
        return idCmd-idCmdFirst # Must return number of menu items we added.

    def InvokeCommand(self, ci):
        mask, hwnd, verb, params, dir, nShow, hotkey, hicon = ci
        CountDirs(self.folder)
        '''
        handle = win32process.CreateProcess(os.path.join(win32api.GetSystemDirectory(),"cmd.exe"),
                '', None, None, 0,
                win32process.CREATE_NEW_CONSOLE, 
                None , 
                self.folder,
                win32process.STARTUPINFO()
                )
        '''
        
def DllRegisterServer():
    key = _winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT,"Folder\\shellex")
    subkey = _winreg.CreateKey(key, "ContextMenuHandlers")
    subkey2 = _winreg.CreateKey(subkey, "EasyCLOC")
    _winreg.SetValueEx(subkey2, None, 0, _winreg.REG_SZ, ShellExtension._reg_clsid_)
    
    print ShellExtension._reg_desc_, "registration complete."

def DllUnregisterServer():
    try:
        _winreg.DeleteKey(_winreg.HKEY_CLASSES_ROOT,"Folder\\shellex\\ContextMenuHandlers\\EasyCLOC")
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration complete."

if __name__=='__main__':
    register.UseCommandLine(ShellExtension,
                   finalize_register = DllRegisterServer,
                   finalize_unregister = DllUnregisterServer)
                   