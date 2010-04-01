#!/usr/bin/python

import  sys
import  wx
import  wx.aui
import wx.lib.analogclock 	   as ac
import wxaddons.sized_controls as sc
import wx.lib.masked.timectrl  as timectl
import wx.lib.scrolledpanel    as scrolled
import wx.lib.masked           as masked
import wx.lib.mixins.listctrl  as listmix
import os.path

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import logging as log
try:
	log.basicConfig(
		filename = 'SimpleAlarmClock.log',
		filemode = 'w',
		level    = log.DEBUG,
		format   = '[%(asctime)s] [%(levelname)-8s] %(message)s',
		datefmt  = "%m.%d.%Y %H:%M:%S")
except:
	pass

TB_SHOW   = wx.NewId()
TB_CONFIG = wx.NewId()
TB_CLOSE  = wx.NewId()

#---------------------------------------------------------------------------
#
class AlarmerItem():
	def __init__(self, aName = u"起床了"):
		self.Name = aName
		self.Enable = False
		self.InRing = False
		self.SetAlarmTime()
		self.SoundFile = ""
		
	def __repr__(self):
		return "%s(name=%r, hp=%r, sp=%r)" % (self.__class__.__name__, self.Name, self.Enable, self.AlarmTime)
			 
	def SetAlarmTime(self, aTime = wx.DateTime_Now(), aOnce = False):
		self.AlarmTime = aTime.Subtract(wx.DateTime_Today())
		self.Enable    = True
		self.Alarmed   = False 
		self.AlarmOnce = aOnce
		
	def AlarmUp(self, now, ClockInterval):
		if (not self.Enable) or (self.Alarmed == True):
			return False
		if self.InRing == True :
			print "On Ringing: " + self.Name 
			return False
		
		timeNow = now.Subtract(wx.DateTime_Today())
		if timeNow.IsLongerThan(self.AlarmTime):
			clkSpan = wx.TimeSpan(0,0,ClockInterval,500) 
			timeSpan = timeNow.Subtract(self.AlarmTime)
			if timeSpan.IsShorterThan(clkSpan):
				self.Alarmed = True
				print "Alarm Up :" + self.Name 
				return True
			else:
				return False
		else:
			#self.Alarmed = True;
			return False
	
	def AlarmReset(self):
		""" """
		if not self.AlarmOnce :
			self.Alarmed = False
		elif self.Enabled :
			self.Alarmed = False
			
	def AlarmNotify(self, frame=None):
		self.InRing = True
		self.sound = wx.Sound(self.SoundFile)
		self.sound.Play(wx.SOUND_ASYNC | wx.SOUND_LOOP)
		alarmHint = AlarmHintFrame(frame, self)
		alarmHint.Show()
	
	def AlarmDown(self) :
		self.sound.Stop()
		self.InRing = False
		#Alarm Once Stoped
		if self.AlarmOnce :
			self.Enabled = False
			
#---------------------------------------------------------------------------
#
class AlarmerListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
		
        self.CurrItem = -1
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self)
        
    def PopulateList(self):
        self.ClearAll()
     
        self.InsertColumn(0, u"闹铃时间")
        self.InsertColumn(1, u"闹铃名字")

        for AlarmItem in self.Parent.AlamerList:
            index = self.InsertStringItem(sys.maxint, "")
            self.SetStringItem(index, 0, AlarmItem.AlarmTime.Format("%H:%M:%S") )
            self.SetStringItem(index, 1, AlarmItem.Name)
        
    def SetStringItem(self, index, col, data):
        if col in range(2):
            wx.ListCtrl.SetStringItem(self, index, col, data)
            wx.ListCtrl.SetStringItem(self, index, 3+col, str(len(data)))
        else:
            try:
                datalen = int(data)
            except:
                return

            wx.ListCtrl.SetStringItem(self, index, col, data)

            data = self.GetItem(index, col-3).GetText()
            wx.ListCtrl.SetStringItem(self, index, col-3, data[0:datalen])
	
    def OnItemSelected(self, event):
		self.CurrItem = event.m_itemIndex

    def OnItemDeselected(self, event):
		self.CurrItem = -1

#--------------------------------------------------------------------------------------------------------------------------------------------------
class AlarmHintFrame(wx.MiniFrame):
	def __init__(self, parent, aItem):
		wx.MiniFrame.__init__(self, parent, -1, title = u"Alarm Notifier", style = wx.CAPTION )
		
		self.alarmItem = aItem
		
		#CentreOnParent seems does not work as expected
		#self.CentreOnParent()
		if parent.IsShown() :
			newPos = parent.GetPosition()
			newPos.x += 50
			newPos.y += 70
			self.SetPosition(newPos)
		else :
			self.CentreOnScreen(wx.BOTH)
			
		self.CloseAlarmBtn  = wx.Button(self, -1, u"关掉闹铃", size = (190, 80))
		self.RemindLaterBtn = wx.Button(self, -1, u"以后提醒", size = (190, 80))
	
		self.Bind(wx.EVT_BUTTON, self.OnCloseAlarm, self.CloseAlarmBtn)
		self.Bind(wx.EVT_BUTTON, self.OnRemindLater, self.RemindLaterBtn)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.SetMinSize((200,100))
		sizer.Add(self.CloseAlarmBtn,  0, wx.ALL, 5)
		sizer.Add(self.RemindLaterBtn, 0, wx.ALL, 5)
		self.SetSizerAndFit(sizer)
	
		self.RemindInteral  = 60	
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.Timer = wx.Timer(self, -1)
		self.Timer.Start(self.RemindInteral * 1000)
		
		
	def CloseMe(self):
		""" """	
		self.alarmItem.AlarmDown()
		self.Close()

	def OnCloseAlarm(self, event):
		""" """	
		self.CloseMe()
		
	def OnRemindLater(self, event):
		""" """
		self.CloseMe()
	
	def OnTimer(self, event):	
		""" """
		self.CloseMe()
		
#--------------------------------------------------------------------------------------------------------------------------------------------------
class  AlarmEditDialog(sc.SizedDialog):
	def __init__(self, parent):
		sc.SizedDialog.__init__(self, None, -1, u"闹钟编辑", style=wx.DEFAULT_DIALOG_STYLE)
        
		pane = self.GetContentsPane()
		pane.SetSizerType("form")
        
		# row 1
		wx.StaticText(pane, -1, u"名称:")
		self.TextCtrlAlarmType = wx.TextCtrl(pane, -1, u"起床了")
		self.TextCtrlAlarmType.SetSizerProps(expand=True)
        
		# row 2
		wx.StaticText(pane, -1, u"时间:")
		
		# here's how to add a 'nested sizer' using sized_controls
		timePane = sc.SizedPanel(pane, -1)
		timePane.SetSizerType("horizontal")
		timePane.SetSizerProps(expand=True)
		self.TimeCtrlAlarmTime = masked.TimeCtrl(timePane, -1, name="24 hour control", fmt24hr=True)
		h = self.TimeCtrlAlarmTime.GetSize().height
		spin = wx.SpinButton( timePane, -1, wx.DefaultPosition,  (-1,h), wx.SP_VERTICAL )
		self.TimeCtrlAlarmTime.BindSpinButton(spin)

		#row
		wx.StaticText(pane, -1, u"声音文件:")
		filePane = sc.SizedPanel(pane, -1)
		filePane.SetSizerType("horizontal")
		filePane.SetSizerProps(expand=True)

		self.TextCtrlAlarmFile = wx.TextCtrl(filePane, -1, "", size = (100, 24))
		SelectFileBtn = wx.Button(filePane, -1, "...", size = (23,23))
		#SelectFileBtn.SetSizerProps(expand=True)  
		#self.TextCtrlAlarmFile.SetSizerProps(expand=True)
		self.Bind(wx.EVT_BUTTON, self.OnSelectSoundFile, SelectFileBtn)
		
		# row	
		wx.StaticText(pane, -1, u"类型:")

		# here's how to add a 'nested sizer' using sized_controls
		radioPane = sc.SizedPanel(pane, -1)
		radioPane.SetSizerType("horizontal")
		radioPane.SetSizerProps(expand=True)

		# make these children of the radioPane to have them use
		# the horizontal layout
		self.EveryDayBtn = wx.RadioButton(radioPane, -1, u"每天提醒")
		self.OnceBtn     = wx.RadioButton(radioPane, -1, u"提醒一次")

		# add dialog buttons
		self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

		# a little trick to make sure that you can't resize the dialog to
		# less screen space than the controls need
		self.Fit()
		self.SetMinSize(self.GetSize())
	
	def SetModalData(self, aItem):
		""" """
		self.TextCtrlAlarmType.SetValue(aItem.Name)
		self.TimeCtrlAlarmTime.SetValue(aItem.AlarmTime)
		self.TextCtrlAlarmFile.SetValue(aItem.SoundFile)
		self.EveryDayBtn.SetValue(not aItem.AlarmOnce)
		self.OnceBtn.SetValue(aItem.AlarmOnce)
		
	def GetModalData(self, aItem):
		""" """
		aItem.Name = self.TextCtrlAlarmType.GetValue()
		tm = self.TimeCtrlAlarmTime.GetValue(as_wxDateTime=True)
		aTime = wx.DateTime_Now()
		aTime.SetHour(tm.GetHour())
		aTime.SetMinute(tm.GetMinute())
		aTime.SetSecond(tm.GetSecond())
		aItem.SetAlarmTime(aTime)
		
		aItem.SoundFile = self.TextCtrlAlarmFile.GetValue()
		
		aItem.AlarmOnce = not self.EveryDayBtn.GetValue()
		
	def OnSelectSoundFile(self, event):
		""" """
		dlg = wx.FileDialog( self, message="Choose a file",
							defaultDir=os.getcwd(), 
							defaultFile=self.TextCtrlAlarmFile.GetValue(),
							wildcard= "*.wav",
							style=wx.OPEN | wx.CHANGE_DIR
							)

		if dlg.ShowModal() == wx.ID_OK:
			self.TextCtrlAlarmFile.SetValue(dlg.GetPath())

		
#--------------------------------------------------------------------------------------------------------------------------------------------------
class ClockFrame(wx.Frame):
    
	def __init__(self, parent, id=-1, title=u"简易小闹钟", pos=wx.DefaultPosition, size=(300,400), 
					style = wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP):
					#style =wx.FRAME_SHAPED | wx.SIMPLE_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP ) :
						 
		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		
		#self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) 
		
		#SysTray Icon Setup
		self.taskBarIcon = wx.Icon(os.path.join("..", "Resource", "Clock.ico"), wx.BITMAP_TYPE_ICO)
		self.tb = wx.TaskBarIcon()
		self.tb.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)
		
		self.SetIcon(self.taskBarIcon)
		
		#self.tb.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnShow)
		self.tb.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnShow)
		
		wx.EVT_MENU(self.tb, TB_SHOW,   self.OnShow)
		wx.EVT_MENU(self.tb, TB_CONFIG, self.OnConfig)
		wx.EVT_MENU(self.tb, TB_CLOSE,  self.OnExit)
		
		#Setup Timer and TimerList
		self.LastClockTime = wx.DateTime_Now()
		self.ClockInterval = 1
		self.AlamerList = list() 
		
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.Timer = wx.Timer(self, -1)
		self.Timer.Start(self.ClockInterval * 1000)
		
		 # Create Panel and Buttons
		panel = wx.Panel(self,size = (300, 30))
		panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
		panel_sizer.SetMinSize((300,40))
		
		self.AddBtn  = wx.Button(panel, -1, u"添加")
		self.EditBtn = wx.Button(panel, -1, u"修改")
		self.DelBtn  = wx.Button(panel, -1, u"删除")
		
		self.Bind(wx.EVT_BUTTON, self.OnAddAlarmItem, self.AddBtn)
		self.Bind(wx.EVT_BUTTON, self.OnEditAlarmItem, self.EditBtn)
		self.Bind(wx.EVT_BUTTON, self.OnDelAlarmItem, self.DelBtn)
		
		#panel_sizer.AddSpacer(80,10)
		panel_sizer.Add(self.AddBtn, 1, wx.ALL|wx.EXPAND, 5)
		panel_sizer.Add(self.EditBtn, 1, wx.ALL|wx.EXPAND, 5)
		panel_sizer.Add(self.DelBtn, 1, wx.ALL|wx.EXPAND, 5)
		panel.SetSizer(panel_sizer)
		panel.Layout()
		
        #Create Panel and  Analog Clock
		clockPanel = wx.Panel(self,size = (300, 300))
		clockPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
		clockPanelSizer.SetMinSize((300,300))
		self.clock = ac.AnalogClock(clockPanel, size=(250,250), hoursStyle = ac.TICKS_DECIMAL,clockStyle=ac.SHOW_HOURS_TICKS| \
                                           ac.SHOW_HOURS_HAND| \
                                           ac.SHOW_MINUTES_HAND| \
										   ac.SHOW_SECONDS_HAND| \
                                           ac.SHOW_SHADOWS)
		colour = wx.Colour(128, 0, 0)
		self.clock.SetHandFillColour(colour)
		colour = wx.Colour(179, 0, 89)
		self.clock.SetHandBorderColour(colour)
		self.clock.SetTickFillColour(colour)
		self.clock.SetTickBorderColour(colour)
		#colour = wx.Colour(225, 255, 255)
		#self.clock.SetFaceBorderColour(colour)
		#self.clock.SetBackgroundColour(colour)
		colour = wx.Colour(249, 255, 255)
		self.clock.SetFaceFillColour(colour)
		colour = wx.Colour(255, 213, 213)
		self.clock.SetShadowColour(colour)
		self.clock.SetTickFont(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD))

		clockPanelSizer.Add(self.clock, 0, wx.ALL, 25)
		
		#Create AlarmListCtrl
		self.list = AlarmerListCtrl(self, -1, size =(300, 150), style=wx.LC_REPORT)
		self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnEditAlarmItem, self.list)
		self.list.PopulateList()
		
        # Use a sizer to layout the controls, stacked vertically and with
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(clockPanelSizer, 0, wx.ALL, 0)
		sizer.Add(self.list, 0, wx.ALL, 0)
		sizer.Add(panel, 0, wx.ALL, 0)
		self.SetSizerAndFit(sizer)
		
		width, height = self.GetSizeTuple() 
		dispSize = wx.GetClientDisplayRect() 
		newPos = wx.Point()
		newPos.x = dispSize.width - width - 1;
		newPos.y = (dispSize.height - height)/2;
		self.SetPosition(newPos)
		
	def OnAddAlarmItem(self, evt):
		"""　"""
		aItem = AlarmerItem()
		dlg = AlarmEditDialog(self)
		dlg.SetModalData(aItem)
		val = dlg.ShowModal()
		if val == wx.ID_OK:
			dlg.GetModalData(aItem)
			self.AlamerList.append(aItem)
			self.list.PopulateList()
		dlg.Destroy()
		
	def OnEditAlarmItem(self, evt):
		""" """
		if self.list.CurrItem == -1 :
			return
		aItem = self.AlamerList[self.list.CurrItem]
		dlg = AlarmEditDialog(self)
		dlg.SetModalData(aItem)
		val = dlg.ShowModal()
		if val == wx.ID_OK:
			dlg.GetModalData(aItem)
			self.list.PopulateList()	
		dlg.Destroy()
		
	def OnDelAlarmItem(self, evt):
		"""Event handler for the button click."""
		if self.list.CurrItem == -1 :
			return
		del(self.AlamerList[self.list.CurrItem])
		if self.list.CurrItem == self.list.CurrItem :
			self.list.CurrItem = -1
		self.list.PopulateList()
		
	def OnTimer(self, evt): 
		""" """
		now = wx.DateTime_Now()
		#log.debug("On Timer: " + now.Format("%H:%M:%S"))
		timeSpan = now.Subtract(self.LastClockTime)
		self.LastClockTime = now
		
		#Time rollback  or ajusted
		clkSpan = wx.TimeSpan(0,0,int(self.ClockInterval * 2), 0) 
		if timeSpan.IsNegative() or timeSpan.IsLongerThan(clkSpan) :
			print "Time Revised"
			for item in self.AlamerList :
				item.AlarmReset()			
	
		for item in self.AlamerList :
			if item.AlarmUp(now,self.ClockInterval) :
				item.AlarmNotify(self)			
	
	def OnTaskBarRightClick(self, evt):
		""" """
		try:
			menu = wx.Menu()
			menu.Append(TB_SHOW,   u"显示小闹钟")
			menu.Append(TB_CONFIG, u"配置小闹钟")
			menu.Append(TB_CLOSE,  u"退出小闹钟")
			self.tb.PopupMenu(menu)
			menu.Destroy()
		except:
			pass 
			#self.OnException()

	def OnShow(self, evt): 
		""" """
		self.tb.RemoveIcon()
		if self.IsIconized() :
			self.Iconize(False)
		if not self.IsShown() :
			self.Show(True)
		self.Raise()
		
	def OnConfig(self, evt): 
		""" """
		pass
	
	def OnExit(self, evt): 
		""" """
		self.Destroy()
		pass
	
	def OnIconfiy(self, event):
		self.tb.SetIcon(self.taskBarIcon, "Simple Clock")
		self.Hide()
		event.Skip()	
	
	def OnClose(self, event):
		#self.tb.SetIcon(self.taskBarIcon, "Simple Clock")
		#event.Veto() 
		#self.Hide()
		#return False
		return True
		
class MyApp(wx.App):
	def OnInit(self):
		frame = ClockFrame(None)
		self.SetTopWindow(frame)
		frame.Show(True)
		return True

	#def MainLoop(self):
	#	"""MainLoop currently not used. Just place it over here for needed in near future"""
	#	self.looping = True
	#	myEventLoop = wx.EventLoop()
	#	prevEventLoop = wx.EventLoop.GetActive()
	#	wx.EventLoop.SetActive(myEventLoop)
	#	
	#	while self.looping :
	#		# Any other looping code should go here
	#
	#		# Process GUI events last
	#		while myEventLoop.Pending() :
	#			myEventLoop.Dispatch()
	#		
	#		self.ProcessIdle()
	#	
	#	#log.info("System Stoped.")
	#	wx.EventLoop.SetActive(prevEventLoop)
		
#-----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':    
	app = MyApp(redirect=False)
	log.info("SimpleAlarmClock Started.")
	app.MainLoop()
	log.info("SimpleAlarmClock Stoped.")
	
