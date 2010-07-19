
# -*- coding: utf-8 -*-
import  wx

from glob import glob

#---------------------------------------------------------------------------

class LoginDialog(wx.Dialog):
    ID_LOGIN    = wx.NewId() 
    ID_REGISTER = wx.NewId()
    ID_PROXY    = wx.NewId()
    
    def __init__(
            self, parent, ID, title = u"用户登录", size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            ):

        pre = wx.PreDialog()
        #pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer = wx.GridBagSizer(5,5)
        
        # Now continue with the normal construction of the dialog
        # contents
        label = wx.StaticText(self, -1, u"\n登录到消息服务器")
        
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, u" 用户名@服务器:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self._userIDTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
        box.Add(self._userIDTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, u" 该用户登录密码:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self._passwordTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1), style = wx.TE_PASSWORD)
        box.Add(self._passwordTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        self._serverAddrCheckBox = wx.CheckBox(self, -1, u"指定登录服务器") #, (65, 80), (150, 20), wx.NO_BORDER)
        box.Add(self._serverAddrCheckBox, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.Bind(wx.EVT_CHECKBOX, self.OnServerCheckBox, self._serverAddrCheckBox)
        
        self._serverAddrTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
        self._serverAddrTextCtrl.Enable(False)
        box.Add(self._serverAddrTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT|wx.TOP, 10)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btn = wx.Button(self, self.ID_LOGIN, u"  登录系统  ")
        self.Bind(wx.EVT_BUTTON, self.OnButtonPressed, id =  self.ID_LOGIN)
        btn.SetDefault()
        btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_LEFT|wx.ALL, 5)
        btnsizer.AddStretchSpacer()

	btn = wx.Button(self, self.ID_REGISTER, u"  我要注册新帐号  ")
        btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_RIGHT|wx.ALL, 5)
	self.Bind(wx.EVT_BUTTON, self.OnButtonPressed, id =  self.ID_REGISTER)
	
	#btn = wx.Button(self, self.ID_PROXY, u"  代理设定  ")
        #btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_RIGHT|wx.ALL, 5)
	#self.Bind(wx.EVT_BUTTON, self.OnButtonProxyPressed, id =  self.ID_PROXY)
	
	sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def OnServerCheckBox(self, event) :
        self._serverAddrTextCtrl.Enable(event.IsChecked())
            
    def OnButtonPressed(self, event) :
	self.EndModal(event.GetId())
    
    def OnButtonProxyPressed(self, event) :
        pass
	
    def doLogin(self, userName, password, serverAddr) :
        self._userIDTextCtrl.SetValue(userName)
        self._passwordTextCtrl.SetValue(password)
        
        if serverAddr != None :
                self._serverAddrTextCtrl.Enable(True)
                self._serverAddrTextCtrl.SetValue(serverAddr)
                self._serverAddrCheckBox.SetValue(True)
        else :
                self._serverAddrTextCtrl.Enable(False)
                self._serverAddrCheckBox.SetValue(False)
        
        #self.CenterOnScreen(wx.BOTH)
        self.CenterOnParent(wx.BOTH)
                
        # this does not return until the dialog is closed.
        val = self.ShowModal()
        
        userName = self._userIDTextCtrl.GetValue()
        password = self._passwordTextCtrl.GetValue()
        
        if self._serverAddrCheckBox.IsChecked() :
                serverAddr = self._serverAddrTextCtrl.GetValue()
        else :
                serverAddr = None
                
        if val == self.ID_LOGIN:
                return ('login', userName, password, serverAddr)
        elif val == self.ID_REGISTER:
                return ('register', userName, password, serverAddr)
        else :
                return ('none',)
                
#---------------------------------------------------------------------------
