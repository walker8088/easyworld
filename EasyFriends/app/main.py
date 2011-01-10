# -*- coding: utf-8 -*-

import socket, threading 
import wx, wx.aui
#from wx.lib.wordwrap import wordwrap
import wx.lib.flatnotebook as fnb

from chat       import *
from login      import LoginDialog
from taskbar    import *
from roster     import * 
from xmlconsole import XmlConsole
from actions    import *
from setting    import *
from browser    import BrowserPanel

from plugins import *
                
import filemgr

from pyxmpp.all  import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient

from addressbook import AddressBookPanel
from notebook    import *

from glob import glob

import event, imclient
import cchessboard 
                
class MainFrame(wx.Frame) : 
        ID_CONNECT      = wx.NewId()
        ID_DISCONNECT   = wx.NewId()
        
        ID_SHOW_XML_CONSOLE  = wx.NewId()
	ID_SHOW_ADDRESS_BOOK = wx.NewId()
        ID_SHOW_NOTE_BOOK    = wx.NewId()
        ID_SHOW_WORKSPACE    = wx.NewId()
        
        ID_SETUP = wx.NewId()
        ID_EXIT  = wx.NewId()
        
	ID_ABOUT_BOX = wx.NewId()
	
        ID_SHOW_ROSTER_WIN   = wx.NewId()
        ID_SHOW_DEBUG_WIN    = wx.NewId()
        ID_SHOW_CHAT_WIN     = wx.NewId()
        ID_SHOW_TOOLBAR      = wx.NewId()
        ID_SHOW_NOTEPAD      = wx.NewId()
        ID_SHOW_ADDR_BOOK    = wx.NewId()
        
        id2win = { 
                ID_SHOW_CHAT_WIN   : ('chat',  u'交谈'), 
                ID_SHOW_ROSTER_WIN : ('roster',  u'联系人'), 
                #ID_SHOW_TOOLBAR :    ('toolbar', u'工具条'), 
		ID_SHOW_NOTEPAD :    ('notepad', u'记事本'),
		ID_SHOW_ADDR_BOOK :  ('addrbook',u'地址本'),
                ID_SHOW_DEBUG_WIN :  ('debug',   u'调试信息'),
		}
                
        def __init__(self, parent, id, title, pos=wx.DefaultPosition, size=(800,600), 
                        style = wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE ):

                wx.Frame.__init__(self, parent, id, title, pos, size, style)
                
		self.lock = threading.Lock()
		
		self._mgr = wx.aui.AuiManager()
                self._mgr.SetManagedWindow(self)
                
                self._icon = wx.Icon(wx.GetApp().APP_ICON_NAME, wx.BITMAP_TYPE_ICO)
        	self.SetIcon(self._icon)
        	
		glob.imclient = imclient.IMConnection(self) 
		
                self._actions = self.MakeActions()
                
                #self._toolBar     = self.MakeToolBar()
                self._statusBar   = self.CreateStatusBar()
                self._taskBarIcon = TaskBarIcon(self, self._icon, 
						wx.Icon("res/message.ico", wx.BITMAP_TYPE_ICO),
						wx.GetApp().APP_SHOW_NAME)
                    
                # win = self.id2win[self.ID_SHOW_TOOLBAR]
                #self._mgr.AddPane(self._toolBar, wx.aui.AuiPaneInfo().
                #                Name(win[0]).ToolbarPane().Top().Fixed().
                #                LeftDockable(False).RightDockable(False).BottomDockable(False).Show(False))

                self._rosterPanel = RosterPanel(self, -1, wx.DefaultPosition, wx.Size(250, 500))
        	win = self.id2win[self.ID_SHOW_ROSTER_WIN]
                self._mgr.AddPane(self._rosterPanel,  wx.aui.AuiPaneInfo().
                                Name(win[0]).Caption(win[1]).
                                Right().CloseButton(True).BottomDockable(False).TopDockable(False).Show(True))
                
		self._debugPanel = wx.aui.AuiNotebook(self)
		self._logCtrl = wx.TextCtrl(self, -1, '', style = wx.NO_BORDER | wx.TE_MULTILINE)
                self._debugPanel.AddPage(self._logCtrl, u"日志信息")
		self._rawXmlPanel = wx.TextCtrl(self, -1, '', style = wx.NO_BORDER | wx.TE_MULTILINE)
                self._debugPanel.AddPage(self._rawXmlPanel, u"通讯信息")
                
                #self._logCtrl = wx.TextCtrl(self, -1, '', style = wx.NO_BORDER | wx.TE_MULTILINE)
                #self._chatPanel.AddPage(self._logCtrl, u"日志信息")
		
                win = self.id2win[self.ID_SHOW_DEBUG_WIN]
                self._mgr.AddPane(self._debugPanel, wx.aui.AuiPaneInfo().
                                Name(win[0]).CaptionVisible(True).CloseButton(True).MinSize((150,150)).
                                Bottom().LeftDockable(False).RightDockable(False).TopDockable(False).Show(True))
               
                #self._chatBook = wx.aui.AuiNotebook(self)
		#win = self.id2win[self.ID_SHOW_CHAT_WIN]
                #self._mgr.AddPane(self._chatBook, wx.aui.AuiPaneInfo().
                #                Name(win[0]).CaptionVisible(True).CloseButton(True).CloseButton(True).MinSize((150,150)).
                #                Bottom().LeftDockable(False).RightDockable(False).TopDockable(False).Show(True))
                
		self._notepadPanel = NoteBookPanel(self)
		win = self.id2win[self.ID_SHOW_NOTEPAD]
                self._mgr.AddPane(self._notepadPanel, wx.aui.AuiPaneInfo().
                                Name(win[0]).Caption(win[1]).CloseButton(True).MinSize((150,150)).
                                Right().LeftDockable(True).RightDockable(True).TopDockable(False).Show(False))
                
		self._addrbookPanel = AddressBookPanel(self)
		win = self.id2win[self.ID_SHOW_ADDR_BOOK]
                self._mgr.AddPane(self._addrbookPanel, wx.aui.AuiPaneInfo().
                                Name(win[0]).Caption(win[1]).CloseButton(True).MinSize((150,150)).
                                Right().LeftDockable(True).RightDockable(True).TopDockable(False).Show(False))
                
		self._browserPanel = BrowserPanel(self)
		self._mgr.AddPane(self._browserPanel, wx.aui.AuiPaneInfo().CenterPane())
                
                self._menuBar = self.MakeMenuBar()
                self.SetMenuBar(self._menuBar)
                
		self.standWins = []
		
		self._mgr.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)
		 
                self._mgr.Update()
          
                self.Bind(imclient.EVT_IM_STATUS_CHANGED,   self.onStatusChanged)
                self.Bind(imclient.EVT_IM_PRESENCE_UPDATE,  self.onPresenceUpdate)
        	self.Bind(imclient.EVT_IM_VCARD, 	    self.onVcardReceived)
		self.Bind(imclient.EVT_IM_PRESENCE_CONTROL, self.onPresenceControl)
                self.Bind(imclient.EVT_IM_ROSTER_UPDATE,    self.onRosterUpdate)
                self.Bind(imclient.EVT_IM_CONNECTED,        self.onConnected)
                self.Bind(imclient.EVT_IM_DISCONNECTED,     self.onDisconnected)
                self.Bind(imclient.EVT_IM_AUTHORIZED,       self.onAuthorized)
                self.Bind(imclient.EVT_IM_AUTHENTICATED,    self.onAuthenticated)
                self.Bind(imclient.EVT_IM_REGISTER,         self.onRegisterd)
                self.Bind(imclient.EVT_IM_MESSAGE_RECEIVED, self.onMessageReceived)
                self.Bind(imclient.EVT_IM_RAW_IO, 	    self.onRawIOMessage)
                
		self.Bind(imclient.EVT_IM_PRIVATE_DATA,   self.onPrivateData)
                self.Bind(filemgr.EVT_IM_FILE_TRANSFER,    self.OnFileTransfer)
                #self.Bind(imclient.IM_PRIVATE_RESULT_EVENT, self.onPrivateReslut)
                
		
                for item_id in self.id2win :
			self.Bind(wx.EVT_MENU, self.OnShowWindow, id = item_id)
                
		self.Bind(wx.EVT_MENU, self.OnCmdAbout, id = self.ID_ABOUT_BOX)
                
		self.lastSize = size
		self.lastPos  = pos
		self.lastRect = self.GetRect()
		
                self.Bind(wx.EVT_MOVE,     self.OnMove)
		self.Bind(wx.EVT_SIZE,     self.OnSize)
		self.Bind(wx.EVT_CLOSE,    self.OnClose)
                self.Bind(wx.EVT_ICONIZE,  self.OnIconfiy) 
                self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
		#wx.GetApp().Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
                self._isAuthorized = False
                
		self._sessionMgr = ChatSessionManager(self)
                #self._sessionIndex = -1  
        	
                self.InitPlugins()
                
                self.CenterOnScreen(wx.BOTH)
		#self.SetTransparent(150)
                
                self.firstStartUp = True
		wx.CallAfter(self.doLogin)
		
		self.Bind(wx.EVT_IDLE, self.OnIdle)
	
        #----------------------------------------------------------------------------------------------------------#
        def MakeActions(self) :
                act = Actions(self)
                
                act.AddAction(self.ID_CONNECT, 
                                u'上线', 
                                glob.getBitmap('online'), 
                                self.OnCmdConnect
                                )
                                
                act.AddAction(self.ID_DISCONNECT, 
                                u"离线", 
                                glob.getBitmap('offline'), 
                                self.OnCmdDisconnect,
                                enabled = False
                                )
                
                act.AddAction(self.ID_EXIT, 
                                u"退出系统", 
                                glob.getBitmap('quit'), 
                                self.OnCmdExit
                                )
                
                act.AddAction(self.ID_SETUP, 
                                u"系统设置", 
                                glob.getBitmap('options'), 
                                self.OnCmdSetup
                                )
                
                
                act.AddAction(self.ID_SHOW_NOTE_BOOK, 
                                u"记事本", 
                                glob.getBitmap('notebook'),
                                self.OnCmdNoteBook
                                )
                
		act.AddAction(self.ID_SHOW_ADDRESS_BOOK, 
                                u"通讯录", 
                                glob.getBitmap('addressbook'),
                                self.OnCmdAddressBook
                                )
                                
                act.AddAction(self.ID_SHOW_WORKSPACE, 
                                u"工作区", 
                                glob.getBitmap('workspaces'),
                                self.OnCmdWorkspace
                                )
		
		act.AddAction(self.ID_SHOW_XML_CONSOLE, 
                                u"查看通讯数据", 
                                glob.getBitmap('xmlconsole'),
                                self.OnCmdXmlConsole
                                )
                
                return act
                
        def MakeMenuBar(self):
                mb = wx.MenuBar()
                
                menu = wx.Menu()
                self._actions[self.ID_CONNECT].AppendToMenu(menu)
                self._actions[self.ID_DISCONNECT].AppendToMenu(menu)
                menu.AppendSeparator()
                self._actions[self.ID_SETUP].AppendToMenu(menu)
                menu.AppendSeparator()
                self._actions[self.ID_EXIT].AppendToMenu(menu)
                mb.Append(menu, u"(&F)文件")
                
                menu = wx.Menu()
                for id in self.id2win :
                        win = self.id2win[id]
                        menu.AppendCheckItem(id, win[1])
                        menu.Check(id, self._mgr.GetPane(win[0]).IsShown())
		mb.Append(menu, u"(&W)窗口")
                
                menu = wx.Menu()
                item = menu.Append(-1, u"主页")
                #item = menu.Append(-1, u"在线升级")
                item = menu.Append(self.ID_ABOUT_BOX, u"关于...")
                
		mb.Append(menu, u"(&H)帮助")
                
                return mb
                
                
        def MakeToolBar(self) :
                #tb = self.CreateToolBar( wx.TB_FLAT | wx.TB_HORZ_TEXT | wx.NO_BORDER | wx.TB_NODIVIDER )
		tb = wx.ToolBar(self, -1, style = wx.TB_FLAT | wx.TB_HORZ_TEXT | wx.TB_NODIVIDER )
                
                tb.SetToolBitmapSize(wx.Size(16,16))
                
                self._actions[self.ID_CONNECT].AppendToToolBar(tb)
                self._actions[self.ID_DISCONNECT].AppendToToolBar(tb)        
                
                #tb.AddSeparator()
                #self._actions[self.ID_SHOW_NOTE_BOOK].AppendToToolBar(tb)
                #self._actions[self.ID_SHOW_ADDRESS_BOOK].AppendToToolBar(tb)
                #self._actions[self.ID_SHOW_WORKSPACE].AppendToToolBar(tb)
                #tb.AddSeparator()
                #self._actions[self.ID_SHOW_PERSONAL_INFO].AppendToToolBar(tb)
                #tb.AddSeparator()
                #self._actions[self.ID_SHOW_XML_CONSOLE].AppendToToolBar(tb)
                
                tb.Realize()
		
                return tb
        
        #----------------------------------------------------------------------------------------------------------#
        def OpenUrl(self, url) :
		self._browserPanel.OpenUrl(url)
	#----------------------------------------------------------------------------------------------------------#
        def InitPlugins(self) :
                self.SubjectMsgHandler = {}
                for item in plugin_list :
                        item.RegisterPlugin(self)
                        
        def OnTaskBarClick(self, event) :
                if self.IsIconized():
                        self.Iconize(False)
                if not self.IsShown():
			self.Show(True)
                self.Raise()
                        
        def OnCreateTaskBarPopupMenu(self, taskbar) :
                menu = wx.Menu()
                self._actions[self.ID_CONNECT].AppendToMenu(menu, taskbar, tmp = True)
                self._actions[self.ID_DISCONNECT].AppendToMenu(menu, taskbar, tmp = True)
                menu.AppendSeparator()
                self._actions[self.ID_EXIT].AppendToMenu(menu, taskbar)
                
                return menu

        #----------------------------------------------------------------------------------------------------------#
        def OnContextMenu(self, event):
                menu = wx.Menu(u'显示/隐藏窗口')                
                for id in self.id2win :
                        win = self.id2win[id]
                        menu.AppendCheckItem(id, win[1])
                        menu.Check(id, self._mgr.GetPane(win[0]).IsShown())
                self.PopupMenu(menu)
                menu.Destroy()
               
        def OnCmdConnect(self, event) :
                self.doLogin()
                
        def OnCmdDisconnect(self, event) :
                self.connectWanted = False
                try :
                        glob.imclient.disconnect()
                except Exception, e:
                        print e
                
                self._actions[self.ID_CONNECT].Enable(True)
                self._actions[self.ID_DISCONNECT].Enable(False)
                
        def OnCmdExit(self, event) :	
                self._taskBarIcon.Destroy()
                self._mgr.UnInit()
                self.Destroy()
		wx.GetApp().ExitMainLoop()
        
        def OnCmdSetup(self, event) :	
                dlg = SettingDialog(self)
                dlg.ShowModal()
                
        def OnCmdXmlConsole(self, event) :
                if not self._rawXmlPanel :
                        self._rawXmlPanel = XmlConsolePanel(self)
                index = self._centerNotebook.GetPageIndex(self._rawXmlPanel)
                if index >= 0:
                        self._centerNotebook.SetSelection(index)    
                else :
			self._centerNotebook.AddPage(self._rawXmlPanel, u"XML通讯")
                self._mgr.Update()
			        
	def OnCmdNoteBook(self, event) :
		self._mgr.Update()
		
        def OnCmdAddressBook(self, event) :
		self._mgr.Update()
		
        def OnCmdWorkspace(self, event) :
                #self._chessboardPanel
		return
		self._chessboardPanel = cchessboard.CChessGamePanel(self)
                index = self._centerNotebook.AddPage(self._chessboardPanel, u"中国象棋")
                self._centerNotebook.SetSelection(index)
		self._mgr.Update()
		
        def OnCmdAbout(self, event) :
		info = wx.AboutDialogInfo()
	        info.Name = wx.GetApp().APP_SHOW_NAME
	        info.Version = wx.GetApp().APP_VERSION
	        info.Copyright = "(C) 2008 walker"
	        info.Description = u"Freinds 是一个以即时消息为基础的程序，目标是提供小型Office办公场所的基础协同应用。",
	        info.WebSite = ("http://friends.my.org", "Friends  home page")
	        info.Developers = [ "Walker Li" ]
		
		licenseText = "Free Ware"

	        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

	        # Then we call wx.AboutBox giving it that info object
	        wx.AboutBox(info)
	 
	#----------------------------------------------------------------------------------------------------------#
        def OnMove(self, event):
		self.lock.acquire()
		newPos = event.GetPosition()
		if not self.lastPos :
			self.lastPos = newPos
			self.lock.release()
			return
		move_x = newPos.x - self.lastPos.x
		move_y = newPos.y - self.lastPos.y
		win = self._sessionMgr.chatWindow
		pos = win.GetPosition()
		pos.x += move_x
		pos.y += move_y
		win.Move(pos)
		self.lastPos = newPos
		self.lock.release()
		
	def OnSize(self, event):
		self.lock.acquire()
		newSize = event.GetSize()
		if not self.lastSize :
			self.lastSize = newSize
			self.lastRect = self.GetRect()
			self.lock.release()
			return
		delta_x = newSize[0] - self.lastSize[0] 
		delta_y = newSize[1] - self.lastSize[1]
		
		win = self._sessionMgr.chatWindow
		pos = win.GetPosition()
		rect = self.lastRect
		wrect = win.GetRect()
		
		left_dist = wrect[0] - rect[0]
		right_dist = rect[0] + rect[2] - wrect[0] - wrect[2]
		top_dist = wrect[1] - rect[1]
		bottom_dist = rect[1] + rect[3] - wrect[1] - wrect[3]
		
		#print left_dist, '<-->', right_dist
		#print top_dist, '<-->', bottom_dist
		
		if left_dist > right_dist:
			posx = pos.x + delta_x
		else :
			posx = pos.x
		
		if top_dist > bottom_dist:
			posy = pos.y + delta_y
		else :
			posy = pos.y
		win.Move((posx, posy))
		
		self.lastSize = newSize
		self.lastRect = self.GetRect()
		self.lock.release()
	
	def Show(self, show) :
		wx.Frame.Show(self, show)
		if show :
			for win in self.standWins :
				if not win.IsShown() :
					win.Show()
			self.standWins = []		
		else :
			win = self._sessionMgr.chatWindow
			if win.IsShown() :
				win.Show(False)
				self.standWins.append(win)
			
        def OnIconfiy(self, event):
		#if not self.IsIconized():
                #        self.Show(False)
		if event.Iconized() :
			print "iconfiy"
                	self.Show(False)
		else :
			print "iconfiy restore"
                		
        def OnClose(self, event):
		print "close"
		self.Show(False)
		event.Veto()
		
	def OnShowWindow(self, event) :
                id = event.GetId()
                show = event.IsChecked()      
                try :
                        win = self.id2win[id][0]
                except :
                        print "error in OnShowWindow"
                        return        
                if show :        
                        self._mgr.GetPane(win).Show()
                else :
                        self._mgr.GetPane(win).Hide()                
                self._menuBar.Check(id, show)
		self._mgr.Update()
                
        def OnPaneClose(self, event):
                win_name = event.GetPane().name
                for id in self.id2win :
			name, caption = self.id2win[id]
			if name == win_name:
				self._menuBar.Check(id, False)
		 
	def OnActivate(self, event) :
		if event.GetActive() :
			self._taskBarIcon.MessageHandled()
			
	def OnIdle(self, event) :
		pass
        #----------------------------------------------------------------------------------------------------------#
        
        def onConnected(self, event) :
                self.updateConnectStatus(u'连接已建立')
                
                self._actions[self.ID_CONNECT].Enable(False)
                self._actions[self.ID_DISCONNECT].Enable(True)
                
        def onAuthorized(self, event) :
                self.updateConnectStatus(u'用户已授权(Authorized)')
                self._isAuthorized = True
                self._rosterPanel.notifyOnline()
		
		glob.on_online()
		
        def onAuthenticated(self, event) :
                self.updateConnectStatus(u'连接已认证(Authenticated)')
        
        def onRegisterd(self, event) :
                if event.result :
                        self.updateConnectStatus(u'用户注册成功,连接建立中...')
                        self.connectWanted = False
                        try :
                                glob.imclient.disconnect()
                        except Exception, e:
				print e
                        self.reconnectToServer()
                else :
                        self.updateConnectStatus(u'用户注册失败,请重新注册')
                        self.doLogin()
                        
        def onDisconnected(self, event) :
	        glob.on_offline()
		self.updateConnectStatus(u'连接已断开')
                self._actions[self.ID_CONNECT].Enable(True)
                self._actions[self.ID_DISCONNECT].Enable(False)
                self._rosterPanel.notifyOffline()
		if not self.connectWanted :
                        return 
                if not self._isAuthorized :
                        wx.CallAfter(self.doLogin)
                elif glob.auto_reconnect:
                        self.updateConnectStatus(u'重新连接中...')
                        wx.CallAfter(self.reconnectToServer)
                
        def onStatusChanged(self, event) :
                s =  "%s %r" % (event.state,event.arg)
                self._statusBar.SetStatusText(s, 0)
                #self.updateConnectStatus(u'状态改变为 : %s' % (s,))
                
        def onRosterUpdate(self, event) :
                self.updateConnectStatus(u'收到联系人信息')
                self._rosterPanel.OnRosterUpdate(event)
        
        def onMessageReceived(self, event) :
                #self.updateConnectStatus(u'收到消息')
		msg = event.stanza
                fromjid = msg.get_from()
        	body = msg.get_body() 
        	if not body :	
			#print "receive empty body msg :", msg.serialize()
        		return
		
                #if not self.IsShown():
		#	self.Show(True)
                elif not self.IsActive() and not self._sessionMgr.IsCharWinActive() :
			self._taskBarIcon.MessageIncoming()
			self.RequestUserAttention()
		jid = JID(fromjid.node, fromjid.domain)
                sItem = self._sessionMgr.activeChatSession(jid)
                sItem.addHistoryText(fromjid, msg.get_body())        
			
        def onRawIOMessage(self, event) :
        	io   = event.IOType
        	data = unicode(event.Data.decode('utf-8', 'ignore'))
        	        
	        if self._mgr.GetPane('debug').IsShown() :	
	                if io == 'IN' :
				color = '#CC3333'
			elif io == 'OUT' :
				color = '#3366CC'
			else :
				print "error message io type"
				return
			self._rawXmlPanel.AppendText(io + ' : ' + data + '\n')
				
        def onPresenceControl(self, event) :
        	stanza = event.stanza 
        	jid = stanza.get_from()
                
                dlg = RosterAcceptDialog(self)
                
                result = dlg.askAddRoster(jid, "")
                if result[0] == 'accept' :                
        	        event.result = 'accept'
			
        	elif result[0] == 'accept_add' :
                        event.result = 'accept'
                        glob.imclient.addRoster(jid, result[1], result[2])
                else :
                        event.result = 'deny'
                
		if event.result == 'accept' :
			p=stanza.make_accept_response()
		else :
			p=stanza.make_deny_response()
		glob.imclient.stream.send(p)
		
        def onPresenceUpdate(self, event) :
                stanza = event.stanza
		
		t=stanza.get_type()
                if t=="unavailable":
                    typestr = u"offline"
                else:
                    typestr = u"online"
		    
		show=stanza.get_show()
                if not show:
			show = ''
			
		#msg = u'更新联系人出席状态信息( %s : %s : %s )' % (stanza.get_from(), typestr, show)
		#self.updateConnectStatus(msg)                
                msg = str(stanza) 
                self._rosterPanel.OnPresenceUpdate(event)
        
	def onVcardReceived(self, event) :
		#stanza = event.stanza
	        #msg = u'更新联系人VCARD信息( %s )' % (stanza.get_from(),)
		#self.updateConnectStatus(msg)    
                self._rosterPanel.OnVcardUpdate(event)	
        
	def onPrivateData(self, event) :
		if self._notebookPanel :
			self._notebookPanel.OnPrivateData(event)
		
        def onPrivateResult(self, event) :
		pass
	
	def OnFileTransfer(self, event) :
		session = event.session
		if event.request == 'open' :
			chat_session = self._sessionMgr.activeChatSession(session.to_jid.bare())	
			chat_session.appendFileTransferSession(session)
        #----------------------------------------------------------------------------------------------------------#
        
        def updateConnectStatus(self, msg) :
                self._statusBar.SetStatusText(msg)
                self._logCtrl.AppendText(msg + "\n")
                
        def doLogin(self) :
                self.connectWanted = True
                self._isAuthorized = False
                dlg = LoginDialog(self, -1)
		
		(userID, password, serverAddr) =  glob.getUserAccount()
                if self.firstStartUp and password != '' :
			self.firstStartUp = False
			result = ('login', userID, password, serverAddr)
		else :
			result = dlg.doLogin(userID, password, serverAddr)
                #print result
                if result[0] == 'login' or result[0] == 'register': 
        		userID = result[1]
        		password = result[2]
        		serverAddr = result[3]
                        
			glob.setUserAccount(userID, password, serverAddr)
			
			glob.save_config()
                        
			#del glob.imclient
			#glob.imclient = imclient.IMConnection(self)     			
        		glob.imclient.setUserAccount(userID, password, socket.gethostname())
			self.updateConnectStatus(u'连接到服务器...')
        		if serverAddr :
                                glob.imclient.setServer(serverAddr)
			else :
				glob.imclient.setServer(None)
                        if result[0] == 'register' :
                                register = True
                        else :
                                register = False
                        try:
				glob.imclient.connect(register)
                        except  Exception, e:
                                self.updateConnectStatus(u'不能连接到服务器 : %s' % (str(e),))				
                #dlg.Destroy()
                
        def reconnectToServer(self) :
                #del glob.imclient
                #glob.imclient = imclient.IMConnection(self)  
		(userID, password, serverAddr) =  glob.getUserAccount()		
                glob.imclient.setUserAccount(userID, password, socket.gethostname())
                if serverAddr :
                        glob.imclient.setServer(serverAddr)
                try :        
			glob.imclient.setServer(None)
			glob.imclient.connect()
                except  Exception, e:
                        self.updateConnectStatus(u'不能连接到服务器 : %s' % (str(e),))				
        	
	'''            
        def load_game_list(self):
                """Locate the games' engines, load them and show them in the games list.
                
                The engines are searched in a couple of locations: the 'games' subdirectory of the
                working directory and an user directorie dependant of the OS.
                For further reference, the engines will be loaded in the engineDict structure
                of Jubatu's root class."""
                logging.getLogger("core").debug("Starting the search for game engines.")
                gameDirs = util.get_game_dirs()
                gameModules = []

                for dir in gameDirs:
                    logging.getLogger("core").info("Looking for engines in dir %s", dir)
                    for item in os.listdir(dir):
                        fullPathItem = os.path.join(dir,item)
                        if os.path.isdir(fullPathItem):
                            entryPoint = os.path.join(fullPathItem, "jubatugame.py")
                            if (os.path.isfile(entryPoint)):
                                fp, pathname, description = imp.find_module(item,[dir])
                                try:
                                    imp.load_module(item, fp, pathname, description)
                                finally:
                                    if fp:
                                        fp.close()
                                module = imp.load_source(item, entryPoint)
                                
                                gameModules.append(module)
                                logging.getLogger("core").debug("Game found: %s\n%s", module.gameEngine.name(), module.gameEngine.description())
                
                for game in gameModules:
                    self.gamesListBox.Append(game.gameEngine.name(), game.gameEngine)  # The engine itself is the associated data
                    wx.GetApp().engineDict[game.gameEngine.id()]=game.gameEngine
                    #game.gameEngine.start()
                    
                # inicializa la selección
                if self.gamesListBox.GetCount() > 0:
                    self.gamesListBox.Select(0)
                    self.gameInfoTextCtrl.SetValue(gameModules[0].gameEngine.description())
                    
                self.rosterTreeCtrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.buddy_selected)
    
        def game_selected(self, event):
                """Triggered when the user click a game in the games list"""
        
                self.gameInfoTextCtrl.SetValue(event.GetClientData().description())
        
                engineId = self.get_selected_engine_id()

                (buddyNode, cookie) = self.rosterTreeCtrl.GetFirstChild(self.rosterRoot)
                while buddyNode and buddyNode.IsOk():
                    self.update_status_icon(buddyNode, engineId)

                    (resource, cookieRes) = self.rosterTreeCtrl.GetFirstChild(buddyNode)
                    while resource and resource.IsOk():
                        self.update_status_icon(resource, engineId)
                        (resource, cookieRes) = self.rosterTreeCtrl.GetNextChild(buddyNode, cookieRes)
                    (buddyNode, cookie) = self.rosterTreeCtrl.GetNextChild(self.rosterRoot, cookie)
                
                event.Skip()
                
        def new_game(self, event):
                """Ask the corresponding engine to open the 'new game proposal' panel"""
                
                logging.getLogger("core").debug("Ready to ask to open the 'new game proposal' panel to engine: %s", event.GetClientData().name())
                ngp = newgamebase.NewGameBasePanel(parent=self.mainNotebook)
                ngp.gameDescriptionLabel.SetLabel(event.GetClientData().description())
                ngp.GetSizer().Insert(0, event.GetClientData().new_game_panel(ngp), 1, wx.EXPAND, 0)
                self.mainNotebook.AddPage(ngp, event.GetClientData().name(), True)
                event.Skip()
        '''    
# end of class MainFrame
