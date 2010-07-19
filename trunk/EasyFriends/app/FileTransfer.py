# 
# This file is used for the wx.HtmlWindow demo.
#

# -*- coding: utf-8 -*-

import  sys
import  wx
import  wx.html as  html
#import  wx.lib.hyperlink as hl

#import wx.lib.sized_controls as sc
#----------------------------------------------------------------------

class FileTransferPanel(wx.Panel):
    ID_ACCEPT = wx.NewId()
    ID_DENY   = wx.NewId()
    ID_CANCEL = wx.NewId()
    
    def __init__(self, parent, id, size=wx.DefaultSize, bgcolor=None):
        wx.Panel.__init__(self, parent, id, size=size)
	
        if bgcolor:
            self.SetBackgroundColour(bgcolor)
	
	sizer = wx.BoxSizer(wx.VERTICAL)
                
        # row 2
        self.name =  wx.StaticText(self, -1, u"", size = (-1,25))
        sizer.Add(self.name, 0, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5)
	
        self.progress = wx.Gauge(self, -1, 100, size = (-1, 25))
        sizer.Add(self.progress, 0, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
	
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
	
	self.btnAccept = wx.Button(self, self.ID_ACCEPT, u"  接受  ")
	btnsizer.Add(self.btnAccept, 0, wx.GROW|wx.ALIGN_RIGHT|wx.ALL, 2)
	self.Bind(wx.EVT_BUTTON, self.OnCmdAccept, id =  self.ID_ACCEPT)
	
	self.btnDeny = wx.Button(self, self.ID_DENY, u"  拒绝  ")
	btnsizer.Add(self.btnDeny, 0, wx.GROW|wx.ALIGN_LEFT|wx.ALL, 2)
	self.Bind(wx.EVT_BUTTON, self.OnCmdDeny, id =  self.ID_DENY)
	
	btnsizer.AddStretchSpacer()

	self.btnCancel = wx.Button(self, self.ID_CANCEL, u"取消")
	btnsizer.Add(self.btnCancel, 0, wx.GROW|wx.ALIGN_RIGHT|wx.ALL, 2)
	self.Bind(wx.EVT_BUTTON, self.OnCmdCancel, id =  self.ID_CANCEL)
	
	sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 2)
	
	self.SetSizer(sizer)
	
	self.session = parent.GetParent().transfers[id]
	
	try :
		if self.session.is_send :
			self.name.SetLabel(u"发送文件[ %s ]到 %s" % (self.session.file_name, self.session.to_jid.as_unicode()))
			self.btnAccept.Disable() 
			self.btnDeny.Disable() 	
			if self.session.status in ['send_error', 'close'] :
				self.btnCancel.Disable()
			else :
				self.btnCancel.Enable()
				
		else :
			self.name.SetLabel(u"%s 请求发送文件[ %s ]" % (self.session.to_jid.as_unicode(), self.session.file_name))
			if self.session.status != 'wait_accept' : 
				self.btnAccept.Disable() 
				self.btnAccept.Disable()
				self.btnCancel.Enable()
			else :
				self.btnCancel.Enable()
		
		if self.session.status in ['sending', 'receiving'] : 
			self.progress.SetValue(self.session.get_progress())
			
	except Exception, e :
		print e	
	self.session.monitor = self
	
    def OnCmdAccept(self, event):
        #name = self.name.GetValue()
        self.btnAccept.Disable() 
	self.btnDeny.Disable() 
	self.btnCancel.Enable() 
	self.session.send_si_response(True)
	
    def OnCmdDeny(self, event):
        self.btnAccept.Disable() 
	self.btnDeny.Disable() 
	self.btnCancel.Enable() 
	self.session.send_si_response(False)
	
    def OnCmdCancel(self, event):
        #name = self.name.GetValue()
        self.session.cancel()
	self.btnAccept.Disable() 
	self.btnDeny.Disable() 
	self.btnCancel.Disable() 
	
    def on_progress(self, session, progress) :   
	self.progress.SetValue(progress)
	
    def on_error(self, session) :   
	self.btnAccept.Disable() 
	self.btnDeny.Disable() 
	self.btnCancel.Enable() 
	pass
    
    def on_close(self, session) :   
	self.btnCancel.Disable() 
	pass
	 	
#----------------------------------------------------------------------



