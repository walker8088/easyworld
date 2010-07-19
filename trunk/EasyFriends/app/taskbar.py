
import wx
 
# ############################################################                
class TaskBarIcon(wx.TaskBarIcon):
	def __init__(self, frame, icon, iconMsg, tooltip):
		wx.TaskBarIcon.__init__(self)
		
                self.icon = icon
		self.iconMsg = iconMsg
		self.tooltip = tooltip
		self.frame = frame
		self.SetIcon(self.icon, self.tooltip)
		
		self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnTaskBarClick)
		#self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
                self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.timer = wx.Timer(self)
		self.timeCount = 0
		
	def OnTaskBarClick(self, event):
		self.frame.OnTaskBarClick(event)
            
        # override
	def CreatePopupMenu(self):
		return self.frame.OnCreateTaskBarPopupMenu(self)
        
	def MessageIncoming(self) :
		self.SetIcon(self.iconMsg, self.tooltip)
		self.timer.Start(1000)
		self.timeCount = 0
		
	def MessageHandled(self) :
		self.SetIcon(self.icon, self.tooltip)
		self.timer.Stop()
		
	def OnTimer(self, event) :
		self.timeCount += 1
		if self.timeCount % 2 == 1 :
			self.SetIcon(self.icon, self.tooltip)
		else :
			self.SetIcon(self.iconMsg, self.tooltip)
		
# ############################################################                
                