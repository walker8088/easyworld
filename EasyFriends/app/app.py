#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path, sys, logging, locale, codecs
import wx

#from twisted.internet import wxreactor
#wxreactor.install()
#from twisted.internet import reactor

from glob import glob    
import main, event, imclient

# ############################################################                
class Application(wx.App):

        APP_NAME        = 'Friends'
        APP_SHOW_NAME   = 'Friends Application'
        APP_ICON_NAME   = 'Friends.ico'
        APP_VERSION     = 'Version 0.8'
        APP_CONFIG_FILE = 'Friends.cfg'
        APP_LOG_FILE    = 'Friends.log'

        def OnInit(self):
                wx.InitAllImageHandlers()
		
		self.configPath()
		self.configLogger()
		logging.info("friends started")
		self.configAutoStart()
		
		glob.mainFrame = main.MainFrame(None, -1, self.APP_SHOW_NAME)
                self.SetTopWindow(glob.mainFrame)
		if len(sys.argv) == 2 and sys.argv[1] == "autostart" :
			glob.mainFrame.Show(False)
                else :
			glob.mainFrame.Show(True)
		
		self.Bind(wx.EVT_QUERY_END_SESSION, self.OnQuerySystemShutDown)
		self.Bind(wx.EVT_END_SESSION, self.OnSystemShutDown)

                self.timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.OnTimer)
                self.timer.Start(100, False)
                       
                return True
        
	def RunApp(self):
		self.MainLoop()
	
	def RunAppWithinTwisted(self, reactor) :
                reactor.registerWxApp(self)
                reactor.run()
        
	def configPath(self) :
		scriptPath = os.path.dirname(__file__)
		sys.path.insert(0, scriptPath)
		scriptPath = os.getcwd()
		sys.path.insert(0, scriptPath)
		
	def configLogger(self) :
		locale.setlocale(locale.LC_CTYPE,"")
                encoding=locale.getlocale()[1]
                
                if not encoding:
                        encoding="gb2312"
                
                sys.stdout=codecs.getwriter(encoding)(sys.stdout,errors="replace")
                sys.stderr=codecs.getwriter(encoding)(sys.stderr,errors="replace")

                logger=logging.getLogger()
                logger.addHandler(logging.StreamHandler())
                
		glob.load_config(self.APP_CONFIG_FILE)
                if glob.config['System']['debug'] == 'yes' :
			logger.setLevel(logging.DEBUG) 
		
	def configAutoStart(self) :
		import _winreg
		
		program = os.path.split(sys.argv[0])[1]
		if program.endswith(".exe") :
			path = os.path.split(sys.argv[0])[0]
			if path == '' :
				param = os.path.join(os.path.pwd(), program)
			else :
				param = sys.argv[0]	
		else :
			mainFile = os.path.split(sys.argv[0]) 
			param = os.path.split(sys.executable)[0] + "\\pythonw.exe " \
				+ os.path.normpath(os.path.join(os.path.dirname(__file__), "..\\", program)) 
		param = param + " autostart"	
		regPath="Software\\Microsoft\\Windows\\CurrentVersion\\Run"	
		key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, regPath, 0, _winreg.KEY_READ | _winreg.KEY_WRITE)
		try :
			oldvalue = _winreg.QueryValueEx(key,'friends')
		except :
			oldvalue = None
			
		if not oldvalue or oldvalue[0] != param :
			_winreg.SetValueEx(key,'friends',0, _winreg.REG_SZ, param)
		
        def OnTimer(self, event):
                if glob.imclient :
                        try :
				glob.imclient.loop_iter()
			except :
				pass
        def OnExit(self) :
                self.timer.Stop()
        
	def OnQuerySystemShutDown(self, event) :
		self.timer.Stop()
		logging.info("system querying shutdown")
		
	def OnSystemShutDown(self, event) :
		logging.info("system shutdown")
	
# end of class Application
# ############################################################                
if __name__ == "__main__":
        app = Application(False)
	app.RunApp()
# ############################################################                
       