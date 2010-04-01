
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import win32con, win32api, win32gui, win32process
import pyHook
import datetime

from ctypes import *

import win32event, winerror

class singleinstance:
    """ Limits application to single instance """

    def __init__(self, name):
        self.mutexname = name
        self.mutex = win32event.CreateMutex(None, False, self.mutexname)
        self.lasterror = win32api.GetLastError()
    
    def aleradyrunning(self):
        return (self.lasterror == winerror.ERROR_ALREADY_EXISTS)
        
    def __del__(self):
        if self.mutex:
            win32api.CloseHandle(self.mutex)

	    
"""
#PSAPI.DLL
psapi = windll.psapi
#Kernel32.DLL
kernel = windll.kernel32

def EnumProcesses():
    arr = c_ulong * 256
    lpidProcess= arr()
    cb = sizeof(lpidProcess)
    cbNeeded = c_ulong()
    hModule = c_ulong()
    count = c_ulong()
    modname = c_buffer(30)
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    
    #Call Enumprocesses to get hold of process id's
    psapi.EnumProcesses(byref(lpidProcess),
                        cb,
                        byref(cbNeeded))
    
    #Number of processes returned
    nReturned = cbNeeded.value/sizeof(c_ulong())
    
    pidProcess = [i for i in lpidProcess][:nReturned]
    
    for pid in pidProcess:
        
        #Get handle to the process based on PID
        hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                      False, pid)
        if hProcess:
            psapi.EnumProcessModules(hProcess, byref(hModule), sizeof(hModule), byref(count))
            psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
            print "".join([ i for i in modname if i != '\x00'])
            
            #-- Clean up
            for i in range(modname._length_):
                modname[i]='\x00'
            
            kernel.CloseHandle(hProcess)


EnumProcesses()
"""

kernel32 = windll.LoadLibrary("kernel32.dll")
psapi = windll.LoadLibrary("Psapi.dll")
ReadProcessMemory = kernel32.ReadProcessMemory
WriteProcessMemory = kernel32.WriteProcessMemory
OpenProcess = kernel32.OpenProcess

pidinfo = {}

def windowEnumerationHandler(hwnd, resultList):
        resultList.append(hwnd)
        return True
        
def EnumTopWindows() :
        hModule = c_ulong()
	count = c_ulong()
	modname = c_buffer(256)
				
	topWindows = []
	
        win32gui.EnumWindows(windowEnumerationHandler, topWindows)
        for hwnd in topWindows:
                (tmp,pid) = win32process.GetWindowThreadProcessId(hwnd)
                if pid not in pidinfo.keys():
                        hProcess = kernel32.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,False, pid)
			if hProcess:
				psapi.EnumProcessModules(hProcess, byref(hModule), sizeof(hModule), byref(count))
				psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
				processName = "".join([ i for i in modname if i != '\x00'])
				for i in range(modname._length_):
					modname[i]='\x00'
				
				win32api.CloseHandle(hProcess)
	                        pidinfo[pid] = (processName, hwnd)
                        
def GetProcessInfo(pid) :
        if pid in pidinfo :
                return pidinfo[pid]
        EnumTopWindows()
        return pidinfo[pid]
        

class ProcessCounter :
	def __init__(self, pid) :
		self.pid = pid
                list = GetProcessInfo(pid)
                self.name = list[0]
                self.hwnd = list[1]
		self.keyCount = 0
		self.mouseClickCount = 0
		
	def __str__(self):
		return "Program (%5d)%s, KeyCount: %d, MouseClick: %d" % (self.pid, self.name, self.keyCount, self.mouseClickCount)

class ProgramCounter :
	def __init__(self, name) :
		self.name = name
		self.pids = {}
		self.keyCount = 0
		self.mouseClickCount = 0
		    
	def AddProcess(self, process) :
		self.pids[process.pid] = process
		
	def Statistics(self, log) :
		self.keyCount = 0
		self.mouseClickCount = 0
		for pid in self.pids :
			process = self.pids[pid]
			self.keyCount += process.keyCount
			self.mouseClickCount += process.mouseClickCount
		log("Program %s, KeyCount: %d, MouseClick: %d" % (self.name, self.keyCount, self.mouseClickCount))
		for pid in self.pids :
			process = self.pids[pid]
			log("          PID:%d, KeyCount: %d, MouseClick: %d" % (process.pid, process.keyCount, process.mouseClickCount))	
	
class ActionCounter :  
        def __init__(self, parent, idleValue = 60) :
		self.parent = parent
                self.pids = {}
		self.keyCount = 0
                self.mouseClickCount = 0
                self.idleCount = 0
                self.activePid = 0
                # create a hook manager
                self.hm = pyHook.HookManager()
                self.hm.KeyDown = self.OnKeyboardEvent
                self.hm.MouseAll = self.OnMouseEvent
        	self.now = datetime.datetime.now()
                self.pidChanged = False
                self.idleValue = idleValue
		self.StartTime = self.now
		
	def IdleClear(self) :
		if self.idleCount >= self.idleValue :
			self.parent.LogAppendAsync(self.now.strftime('%H:%M:%S') + " System Idled for %d Seconds" % self.idleCount)
		self.idleCount = 0
		
	def OnIdle(self):
		self.idleCount += 1
		if self.idleCount == self.idleValue:
			self.activePid = 0
			self.parent.LogAppendAsync(self.now.strftime('%H:%M:%S') + " System Idled")
		
        def OnMouseEvent(self, event):
                self.IdleClear()
		if event.MessageName != 'mouse left down' and  event.MessageName != 'mouse right down':
			return True
		self. mouseClickCount += 1
		
		(tmp,pid) = win32process.GetWindowThreadProcessId(event.Window)
		
                if pid in self.pids :
			#print "mouse active old process ", str(pid)
			pass
		else :
			#print "mouse active new process ", str(pid)
			self.pids[pid] = ProcessCounter(pid)
			
		counter = self.pids[pid]	
		counter.mouseClickCount += 1		
                
                self.ActiveProcess(pid)
		
                #print 'Active App:', appName
                        
                        # called when mouse events are received
                        #print 'MessageName:',event.MessageName

                        #print 'Window:',event.Window
                        #print 'WindowName:',event.WindowName

                # return True to pass the event to other handlers
                return True
                
        def ActiveProcess(self, pid) :	
		if self.activePid != pid :
                        self.pidChanged = True
                        self.parent.LogAppendAsync(self.now.strftime('%H:%M:%S') + " Active (%5d) %s [%s]" % 
					(pid, self.pids[pid].name, win32gui.GetWindowText(self.pids[pid].hwnd)))
                self.activePid = pid
		
        def OnKeyboardEvent(self, event):
                self.IdleClear()
		if event.Ascii != 0:
                        self.keyCount += 1
                (tmp,pid) = win32process.GetWindowThreadProcessId(event.Window)
		if pid in self.pids :
			#print "key active old process ", str(pid)
			pass
		else :
			#print "key active new process ", str(pid)
			self.pids[pid] = ProcessCounter(pid)
			
		counter = self.pids[pid]
		counter.keyCount += 1		
		self.ActiveProcess(pid)
		
                '''        
                print 'MessageName:',event.MessageName
                print 'Window:',event.Window
                print 'WindowName:',event.WindowName
                print 'Ascii:', event.Ascii, chr(event.Ascii)
                print 'Key:', event.Key
                print 'KeyID:', event.KeyID
                print 'ScanCode:', event.ScanCode
                print 'Extended:', event.Extended
                print 'Injected:', event.Injected
                print 'Alt', event.Alt
                print '---'
                '''
                
                # return True to pass the event to other handlers
                return True

	def Start(self) :                                               
                # set the hook
                self.hm.HookKeyboard()
                self.hm.HookMouse()

                # wait forever
                #pythoncom.PumpMessages(1000)
                
        def Stop(self) :
                self.hm.UnHookKeyboard()
                self.hm.UnHookMouse()
        
	def PassedOneSecond(self) :
		self.now = datetime.datetime.now()
		self.OnIdle()
	
	def Statistics(self) :
		timespand = datetime.datetime.now() - self.StartTime
		self.parent.LogAppendAsync("Statistics Begin")
		self.parent.LogAppendAsync("Total Log Time: %s" % (str(timespand)) )
		self.parent.LogAppendAsync("Total Count of Key: %d, MouseClick: %d" % (self.keyCount, self. mouseClickCount) )
		
		prog = {}
		for pid in self.pids :
			process = self.pids[pid]
			if not process.name in prog :
				prog[process.name] = ProgramCounter(process.name)
			p = prog[process.name]
			p.AddProcess(process)
		for name in prog :
			p = prog[name]
			p.Statistics(self.parent.LogAppendAsync)
		#self.parent.LogAppendAsync(str(self.pids[pid]))
                self.parent.LogAppendAsync("Statistics End.")
		
class MyTaskBarIcon(wx.TaskBarIcon):	
	ID_MenuExit = wx.NewId()

	def __init__(self, frame):
		wx.TaskBarIcon.__init__(self)	
		self.frame = frame	
		self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnTaskBarClick)
                self.Bind(wx.EVT_MENU, self.OnMenuExit, id=self.ID_MenuExit)

        def ShowIcon(self, yes = True) :
                if yes :
                        self.SetIcon(wx.Icon(name='EasyActionLog.ico', type=wx.BITMAP_TYPE_ICO), 'Action Log Application')
		elif self.IsIconInstalled():
                        self.RemoveIcon() 
        # override	
        def CreatePopupMenu(self):
		menu = wx.Menu()		
                menu.Append(self.ID_MenuExit, '&Exit')
                return menu
                
	def OnTaskBarClick(self, event):
		if self.frame.IsIconized():
                        self.frame.Iconize(False)
                if not self.frame.IsShown():
			self.frame.Show(True)
		self.frame.Raise()
                #self.ShowIcon(False)
        
        def OnMenuExit(self, event):
		self.frame.ExitApp()
   
class MainFrame(wx.Frame):     
	ID_CLEAR = wx.NewId()
	ID_EXIT  = wx.NewId()
	ID_STATISTIC = wx.NewId()
	TIMER_ID = wx.NewId()
        def __init__(self, parent, id=-1, title="Action Log", pos=wx.DefaultPosition,
                 size=(600, 400), style = wx.DEFAULT_FRAME_STYLE ):

                wx.Frame.__init__(self, parent, id, title, pos, size, style)
                
                icon = wx.Icon("EasyActionLog.ico", wx.BITMAP_TYPE_ICO)
        	self.SetIcon(icon)
        
                sizer = wx.BoxSizer(wx.VERTICAL)
                
                label = wx.StaticText(self, -1, 'Application Action Loger')
                sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.logList = wx.ListBox(self, -1, size = (600, 400), style = wx.LB_SINGLE)
                sizer.Add(self.logList, 1, wx.ALIGN_CENTRE|wx.EXPAND, 5)
        
                btnsizer = wx.BoxSizer(wx.HORIZONTAL)
                
                self.btnStatistics = wx.Button(self, self.ID_STATISTIC, "Statistics")
                btnsizer.Add(self.btnStatistics, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
		self.btnClear = wx.Button(self, self.ID_CLEAR, "Clear Log")
                btnsizer.Add(self.btnClear, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                #self.btnExit = wx.Button(self, self.ID_EXIT, "Exit")
                #btnsizer.Add(self.btnExit, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT|wx.ALL, 3) #wx.ALIGN_CENTER_VERTICAL
               
                self._statusBar = self.CreateStatusBar(1, 0)
           
                self.SetSizer(sizer)
                sizer.Fit(self)
        
                self.SetBackgroundColour(wx.Colour(220, 220, 220))
                self.Center()
                
        	self.taskBarIcon = MyTaskBarIcon(self)
                self.taskBarIcon.ShowIcon(True)
 
                self.Bind(wx.EVT_BUTTON, self.OnBtnClear, self.btnClear)
		self.Bind(wx.EVT_BUTTON, self.OnBtnStatistics, self.btnStatistics)
                #self.Bind(wx.EVT_BUTTON, self.OnClose, self.btnExit)
                self.Bind(wx.EVT_CLOSE, self.OnClose)
                self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) 
         
                self.counter = ActionCounter(self)
                self.counter.Start()
                
		self.timer = wx.Timer(self, self.TIMER_ID)
		wx.EVT_TIMER(self, self.TIMER_ID, self.OnTimer)
		self.timer.Start(1000)  
	
        def LogAppendAsync(self, logString):
                wx.CallAfter(self.LogAppend,logString)
        
	def LogAppend(self, logString) :
		n = self.logList.Append(logString)
		self.logList.Select(n)
		
        def OnTimer(self, event) :
		if self.counter != None:
			self.counter.PassedOneSecond()
	
        def OnBtnClear(self, event) :
                self.logList.Clear()

	def OnBtnStatistics(self, event) :
		if self.counter != None:
			self.counter.Statistics()
		
        def OnIconfiy(self, event):
                self.Hide()
                #self.taskBarIcon.ShowIcon(True)
                
        def OnClose(self, event):
		self.Hide()
		
	def ExitApp(self) :	
		self.timer.Stop()
                self.taskBarIcon.Destroy()
                self.Destroy()
		
class App(wx.App):
        def OnInit(self):
                wx.InitAllImageHandlers()
                mainFrame = MainFrame(None, -1, "ActionLog")
                self.SetTopWindow(mainFrame)
                #mainFrame.Show()
                return 1
# end of class App

if __name__ == "__main__":
	instance = singleinstance("MY_ACTION_LOG_APPLICATION")
	if not instance.aleradyrunning() :
		app = App(0)
		app.MainLoop()
	del instance
		

