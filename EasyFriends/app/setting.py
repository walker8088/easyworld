
# -*- coding: utf-8 -*-

import  wx

from glob import glob

# ############################################################                
class ConfigBook(wx.Treebook):
	def __init__(self, parent, id = -1):
		wx.Treebook.__init__(self, parent, id, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                            )
		p1 = wx.Panel(self)
		self.AddPage(p1, u'一般')
		p2 = wx.Panel(self)
		self.AddPage(p2, u'通知')
		p3 = wx.Panel(self)
		self.AddPage(p3, u'文件传输')
		p4 = wx.Panel(self)
		self.AddPage(p4, u'安全')
		p5 = wx.Panel(self)
		self.AddPage(p5, u'连接')
		
# ############################################################                
class SettingDialog(wx.Dialog):
        def __init__(self, parent, title = u"系统设置", 
                pos=wx.DefaultPosition, size=(500,400), style=wx.DEFAULT_DIALOG_STYLE ) :

                pre = wx.PreDialog()
                #pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
                pre.Create(parent, -1, title, pos, size, style)
                self.PostCreate(pre)

                sizer = wx.BoxSizer(wx.VERTICAL)
                self._book = ConfigBook(self)
                sizer.Add(self._book, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 10)
                
                line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
                sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT|wx.TOP, 10)
		
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
                
                btnsizer.AddStretchSpacer()

                btn = wx.Button(self, -1, u'确定')
                #self.Bind(wx.EVT_BUTTON, self.OnBtnClearHistory, btn)
		btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_RIGHT|wx.RIGHT|wx.LEFT, 10)

                btn = wx.Button(self, -1, u'取消')
                #self.Bind(wx.EVT_BUTTON, self.OnBtnSaveAs, btn)
		btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_RIGHT|wx.RIGHT, 10)
		#btnsizer.AddButton(btn)
		#btnsizer.Realize()

                sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 10)
		
		self.SetSizer(sizer)
		
                #sizer.Fit(self)
                
                self.CenterOnScreen()        
#end class

# ############################################################                
