# -*- coding: utf-8 -*-
import wx, wx.aui
import wx.lib.iewin as iewin

from  glob import *

#----------------------------------------------------------------------
import wx.lib.platebtn as platebtn

class BrowserPanel(wx.Panel):
    ID_BACK    = wx.NewId()
    ID_FORWARD = wx.NewId()
    ID_REFRESH = wx.NewId()
    ID_STOP    = wx.NewId()
    ID_CONNECT = wx.NewId()
    ID_HOME    = wx.NewId()
    
    ID_ONLINE  = wx.NewId()
    ID_OFFLINE = wx.NewId()
    
    def __init__(self, parent, frame=None):
        wx.Panel.__init__( self, parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN|wx.NO_FULL_REPAINT_ON_RESIZE )
	    
        self.homeUrl = "http://www.google.cn/"    
	
	if frame == None :
		self.frame = parent
	else :
		self.frame = frame
	
	sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        #self.titleBase = frame.GetTitle()
	
	tsize = (24,24)
	
	tb = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        tb.SetToolBitmapSize(tsize)
        
	#folder = Home.GetBitmap()
	
	#tbtn = platebtn.PlateButton(tb, wx.ID_ANY, u' 连接 ', glob.getBitmap('connect'), style = platebtn.PB_STYLE_SQUARE)
	#menu = wx.Menu()
        #menu.Append(wx.NewId(), u"上线")
        #menu.Append(wx.NewId(), u"离线")
        #tbtn.SetMenu(menu)
        
	#tb.AddControl(menu)
	
	tb.AddLabelTool(self.ID_BACK, u"后退", glob.getBitmap('back'), shortHelp="Go Back", longHelp="Go Back")
        self.Bind(wx.EVT_TOOL, self.OnPrevPageButton, id = self.ID_BACK)
        
	tb.AddLabelTool(self.ID_FORWARD, u"前进", glob.getBitmap('forward'), shortHelp="Go Forward")
        self.Bind(wx.EVT_TOOL, self.OnNextPageButton, id = self.ID_FORWARD)
        
	tb.AddSeparator()
        
	tb.AddLabelTool(self.ID_REFRESH, u"刷新", glob.getBitmap('refresh'), shortHelp="Go Forward")
        self.Bind(wx.EVT_TOOL, self.OnRefreshPageButton, id = self.ID_REFRESH)
        
	tb.AddLabelTool(self.ID_STOP, u"停止", glob.getBitmap('stop'), shortHelp="Go Forward")
        self.Bind(wx.EVT_TOOL, self.OnStopButton, id = self.ID_STOP)
        
	tb.AddSeparator()
        
	tb.AddLabelTool(self.ID_CONNECT, u"连接", glob.getBitmap('connect'), shortHelp="Go Forward")
        self.Bind(wx.EVT_TOOL, self.OnConnectButton, id = self.ID_CONNECT)
        
	tb.AddSeparator()
        
	tb.AddLabelTool(self.ID_HOME, u"主页", glob.getBitmap('home'), shortHelp="Go Home")
        self.Bind(wx.EVT_TOOL, self.OnHomeButton, id = self.ID_HOME)
        
	tb.AddSeparator()
        
	self.location = wx.ComboBox(tb, -1, "", style=wx.CB_DROPDOWN|wx.PROCESS_ENTER)
        self.Bind(wx.EVT_COMBOBOX, self.OnLocationSelect, self.location)
        self.location.Bind(wx.EVT_KEY_UP, self.OnLocationKey)
        self.location.Bind(wx.EVT_CHAR, self.IgnoreReturn)
        tb.AddControl(self.location)
	tb.Realize()
	
	self._toolBar = tb
	sizer.Add(self._toolBar, 0, wx.ALIGN_TOP | wx.EXPAND | wx.ALL, 2)
		
	#self._mgr.AddPane(tb, wx.aui.AuiPaneInfo().Name("toolbar").ToolbarPane().Top().
        #                  Gripper(False).LeftDockable(False).RightDockable(False))
        self.ie = iewin.IEHtmlWindow(self)
	sizer.Add(self.ie, 1, wx.EXPAND)
        self.ie.AddressBar = True

        self.SetSizer(sizer)
	
	'''
        #btn = wx.Button(self, -1, "Search", style=wx.BU_EXACTFIT)
        #self.Bind(wx.EVT_BUTTON, self.OnSearchPageButton, btn)
        #btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)
        self._mgr.AddPane(self.ie, wx.aui.AuiPaneInfo().Name("grid_content").CenterPane())
	
	self._mgr.Update()
	'''
	
	self.toUrl = None
        self.ie.LoadUrl(self.homeUrl)
        self.location.Append(self.homeUrl)

	self.Bind(wx.EVT_SIZE, self.OnSize)
	self.Bind(wx.EVT_IDLE, self.OnIdle)
	
        self.ie.AddEventSink(self)

    def OpenUrl(self, url) :
	self.ie.LoadUrl(url)
	self.location.Append(url)
	
    def OnSize(self, evt):
	self.Layout()
	
	newSize = evt.GetSize()
	
	lcPos = self.location.GetPosition()
	lcSize = self.location.GetSize()
	lcSize[0] = newSize[0] - lcPos[0] - 4
	self.location.SetSize(lcSize)
	
	tbSize = self._toolBar.GetSize()
	tbSize[0] = newSize[0] - 2
	self._toolBar.SetSize(tbSize)
	
    def OnLocationSelect(self, evt):
        url = self.location.GetStringSelection()
        self.ie.Navigate(url)

    def OnLocationKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_RETURN:
            URL = self.location.GetValue()
            self.location.Append(URL)
            self.ie.Navigate(URL)
        else:
            evt.Skip()

    def IgnoreReturn(self, evt):
        if evt.GetKeyCode() != wx.WXK_RETURN:
            evt.Skip()

    def OnHomeButton(self, event):
        self.ie.LoadUrl(self.homeUrl) 

    def OnPrevPageButton(self, event):
        self.ie.GoBack()

    def OnNextPageButton(self, event):
        self.ie.GoForward()

    def OnCheckCanGoBack(self, event):
        event.Enable(self.ie.CanGoBack())
        
    def OnCheckCanGoForward(self, event):
        event.Enable(self.ie.CanGoForward())

    def OnStopButton(self, evt):
        self.ie.Stop()

    def OnSearchPageButton(self, evt):
        self.ie.GoSearch()

    def OnRefreshPageButton(self, evt):
        self.ie.Refresh(iewin.REFRESH_COMPLETELY)
    
    def OnConnectButton(self, evt) :
	#control = self._toolBar.FindById(self.ID_CONNECT).GetControl()
	#rect = control.GetRect()
	#pos = (rect[0], rect[1] + rect[3])
	
	menu = wx.Menu()                
	menu.Append(self.ID_ONLINE, u'上线')
	menu.Append(self.ID_OFFLINE, u'下线')
        if glob.online :
		menu.Enable(self.ID_ONLINE, False)
	else :
		menu.Enable(self.ID_OFFLINE, False)
	
	self.Bind(wx.EVT_MENU, self.OnCmdOnline,  id=self.ID_ONLINE)
	self.Bind(wx.EVT_MENU, self.OnCmdOffline, id=self.ID_OFFLINE)
	
	self.PopupMenu(menu)
        menu.Destroy()
    
    def OnCmdOnline(self, event) :
	self.GetParent().doLogin()
	
    def OnCmdOffline(self, event) :
	parent = self.GetParent()
	parent.connectWanted = False
        try :
		glob.imclient.disconnect()
        except Exception, e:
                print e
		
    def BeforeNavigate2(self, this, pDisp, Url, Flags, TargetFrameName,
                        PostData, Headers, Cancel):
        #print TargetFrameName[0]
        #self.toUrl = Url[0]
        #Cancel[0] = True
        #print Url[0]
        #print Flags[0]
        #Flags[0]=64
        #print TargetFrameName[0]
        #print PostData[0]
        #print Headers[0]
        #self.ie.LoadUrl(URL[0]) 
        pass

    def OnNewWindow2(self, this, pDisp, Cancel, Flags, urlContext, URL):
        print "OnNewWindow2"
        Cancel[0] = True   # Veto the creation of a  new window.

    def ProgressChange(self, this, progress, progressMax):
	#    self.log.write('ProgressChange: %d of %d\n' % (progress, progressMax))
        pass
	
    def DocumentComplete(self, this, pDisp, URL):
        self.current = URL[0]
        self.location.SetValue(self.current)

    def TitleChange(self, this, Text):
        if self.frame:
            self.frame.SetTitle(Text)  #self.titleBase + ' -- ' + Text)

    def StatusTextChange(self, this, Text):
        if self.frame:
            self.frame.SetStatusText(Text)
	    
    def OnIdle(self, evt) :
        if self.toUrl :
            self.ie.LoadUrl(self.toUrl)
            self.toUrl = None
		