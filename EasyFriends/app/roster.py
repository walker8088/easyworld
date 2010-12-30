
# -*- coding: utf-8 -*-
import os, os.path
import wx
import wx.lib.platebtn as platebtn

from glob import glob
import event, imclient, actions

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient
from pyxmpp.jabber.vcard import VCARD_NS, VCard, VCardString

GENERAL_GROUP_NAME = u'未分组联系人'
OTHER_GROUP_NAME   = u'其他联系人'

# ############################################################                

class PresenceStatusItem :
        status_text = { 
                'chat'    : u'空闲',
		'dnd'     : u'忙碌',
		'away'    : u'离开',
                'xa'      : u'不可用',
                'online'     : u'在线',
                'offline'    : u'离线',
                'available'   : u'在线',
                'unavailable' : u'离线',
                }
                
        def __init__(self, jid, icons) :
                self.jid        = jid
                self.type       = None
                self.show       = None
                self.status     = None
                self.icons      = icons
                self.image_index = -1
                
        def from_presence(self, presence) :
                self.type   = presence.get_type()
		self.show   = presence.get_show()
                self.status = presence.get_status()
                
                if self.type == 'unavailable' :
                        self.image_index = self.icons['offline']
                else :        
                        self.type = 'available'
			if not self.show :
                                self.show = 'online'        
                        self.image_index = self.icons[self.show]
                        
        def get_show_message(self) :
                if self.status :
                        return self.status
                elif self.show in self.status_text:
                        return self.status_text[self.show]
                return self.show
			
# ############################################################                

class PresenceStatus :
        def __init__(self, parent, icons) :
                self.parent = parent
                self.icons  = icons
                
                self.items_dict={}
        
        def __iter__(self):
                return self.items_dict.itervalues()

        def __contains__(self, id):
                return id in self.items_dict

        def __getitem__(self, id):
                return self.items_dict[id]

        def GetPresenceStatus(self):
                """Return a list of items in the roster."""
                return self.items_dict.values()

        PresenceStatus = property(GetPresenceStatus)
        
        def AddPresenceStatus(self, presence):
                jid = presence.get_from()
                item = PresenceStatusItem(jid, self.icons)
                item.from_presence(presence)
                self.items_dict[jid.bare()] = item
                return item
        
        def RemovePresenceStatus(self, id):
                """Remove item from the roster."""
                del self.items_dict[id]
                
        
# ############################################################                
class RosterAddDialog(wx.Dialog):
        def __init__(self, parent, title = u"添加联系人", 
                size=wx.DefaultSize, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE ) :

                pre = wx.PreDialog()
                #pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
                pre.Create(parent, -1, title, pos, size, style)

                self.PostCreate(pre)

                sizer = wx.BoxSizer(wx.VERTICAL)

                box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(self, -1, u"用户名@服务器 : ")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                self._userIDTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
                #text.SetHelpText("Here's some help text for field #1")
                box.Add(self._userIDTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

                box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(self, -1, u"对此人称呼(昵称):")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                self._nickNameTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
                #text.SetHelpText("Here's some help text for field #1")
                box.Add(self._nickNameTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

                box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(self, -1, u"添加到联系人组 : ")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		
		if glob.imclient.roster :
			groups = glob.imclient.roster.get_groups()
			try :
                                groups.remove(None)
                        except :
                                pass
		else :
			groups = ()	
                self._userGroupCtrl = wx.ComboBox(self, -1, size=(180,-1),  choices = groups)
                box.Add(self._userGroupCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

                line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
                sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

                btnsizer = wx.StdDialogButtonSizer()
                
                btn = wx.Button(self, wx.ID_OK)
                btn.SetDefault()
                btnsizer.AddButton(btn)

                btn = wx.Button(self, wx.ID_CANCEL)
                btnsizer.AddButton(btn)
                btnsizer.Realize()

                sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5)

                self.SetSizer(sizer)
                sizer.Fit(self)
		
		self.CenterOnScreen()
		
#end class  RosterAddDialog

# ############################################################                

class RosterAcceptDialog(wx.Dialog):
        ID_DENY       = wx.NewId()
        ID_ACCEPT     = wx.NewId()
        ID_ACCEPT_ADD = wx.NewId()
        
        def __init__(self, parent, title = u"联系人添加确认", 
                size=wx.DefaultSize, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE ) :
                
                pre = wx.PreDialog()
                #pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
                pre.Create(parent, -1, title, pos, size, style)

                self.PostCreate(pre)

                sizer = wx.BoxSizer(wx.VERTICAL)
                #sizer = wx.GridBagSizer(5,5)
                
                # Now continue with the normal construction of the dialog
                # contents
                label = wx.StaticText(self, -1, u"\n该联系系人请求把添加你到他的联系人列表中")
                
                sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

                box = wx.BoxSizer(wx.HORIZONTAL)

                label = wx.StaticText(self, -1, u"用户名@服务器 : ")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                self._userNameTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
                self._userNameTextCtrl.Enable(False)
		box.Add(self._userNameTextCtrl, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(self, -1, u"对此人称呼(昵称):")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                self._nickNameTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
                #text.SetHelpText("Here's some help text for field #1")
                box.Add(self._nickNameTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

                box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(self, -1, u"添加到联系人组 : ")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		
		if glob.imclient.roster :
			groups = glob.imclient.roster.get_groups()
			try :
				groups.remove(None)
			except :
				pass
		else :
			groups = ()	
			
                self._userGroupCtrl = wx.ComboBox(self, -1, size=(180,-1),  choices = groups)
                box.Add(self._userGroupCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

                line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
                sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
               
                btnsizer = wx.BoxSizer(wx.HORIZONTAL)
                btn = wx.Button(self, self.ID_DENY, u"  拒绝  ")
                self.Bind(wx.EVT_BUTTON, self.OnButtonPressed, id =  self.ID_DENY)
                btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_LEFT|wx.ALL, 5)
                btnsizer.AddStretchSpacer()

        	btn = wx.Button(self, self.ID_ACCEPT, u"  接受  ")
                btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_RIGHT|wx.ALL, 5)
        	self.Bind(wx.EVT_BUTTON, self.OnButtonPressed, id =  self.ID_ACCEPT)
        	
        	btn = wx.Button(self, self.ID_ACCEPT_ADD, u"  接受并添加  ")
                btn.SetDefault()
		btnsizer.Add(btn, 0, wx.GROW|wx.ALIGN_RIGHT|wx.ALL, 5)
        	self.Bind(wx.EVT_BUTTON, self.OnButtonPressed, id =  self.ID_ACCEPT_ADD)
        	
        	sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5)
                
                self.SetSizer(sizer)
                sizer.Fit(self)
                
		self.CenterOnScreen()
		
        def OnGroupSelectCheckBox(self, event) :
                self._groupNameTextCtrl.Enable(event.IsChecked())
                
        def OnButtonPressed(self, event) :
                self.EndModal(event.GetId())
        
        def askAddRoster(self, jid, msg) :
        
                # this does not return until the dialog is closed.
                self._userNameTextCtrl.SetValue(jid.as_unicode())
                self._nickNameTextCtrl.SetValue(jid.node)
                
                val = self.ShowModal()
		
                nickName = self._nickNameTextCtrl.GetValue()
		groupName = self._userGroupCtrl.GetValue()
		
                if val == self.ID_ACCEPT:
                        return ('accept',)
                elif val == self.ID_ACCEPT_ADD:
                        return ('accept_add', nickName, groupName)
                else :
                        return ('deny',)
                
        
#end class  RosterAcceptDialog
# ############################################################
import wx.lib.sized_controls as sc

class MyInfoDialog(sc.SizedDialog):
    def __init__(self, parent, id = -1):
        sc.SizedDialog.__init__(self, None, -1, u"个人基本信息", 
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        
        # row 1
        wx.StaticText(pane, -1, u"姓 名:")
        self.nameCtrl = wx.TextCtrl(pane, -1, size = (250, -1))
        self.nameCtrl.SetSizerProps(expand=True)
        
        # row 2
        wx.StaticText(pane, -1, u"E-Mail:")
        self.emailCtrl = wx.TextCtrl(pane, -1, "")
        self.emailCtrl.SetSizerProps(expand=True)
        
        # row 4
        wx.StaticText(pane, -1, u"电 话:")
        self.phoneCtrl = wx.TextCtrl(pane, -1, '') # two chars for state
        self.phoneCtrl.SetSizerProps(expand=True)
        
        # row 5
        wx.StaticText(pane, -1,  u"手 机:")
        self.mobileCtrl = wx.TextCtrl(pane, -1, '') # two chars for state
        self.mobileCtrl.SetSizerProps(expand=True)
        
	'''
        # here's how to add a 'nested sizer' using sized_controls
        radioPane = sc.SizedPanel(pane, -1)
        radioPane.SetSizerType("horizontal")
        radioPane.SetSizerProps(expand=True)
        '''
        
        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        
        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())
        
	self.CenterOnParent()
    
    def ShowVcard(self, jid) :
	glob.imclient.vard_mgr.query_get(jid, self)
	val = self.ShowModal()
        if val == wx.ID_OK:
		self.vcard.fn = VCardString('FN', self.nameCtrl.GetValue().encode('utf-8'))
		
		glob.imclient.vard_mgr.query_set(self.vcard)	
		
    def on_vcard(self, vcard) :
        self.vcard = vcard
	if vcard.fn.value :
		self.nameCtrl.SetValue(vcard.fn.value)
	
	e = ''
	for email in vcard.email:
	        e += str(email.address) + ";"
	self.emailCtrl.SetValue(e)
	
	e = ''
	for tel in vcard.tel:
	            e += tel.number + ";"
	self.phoneCtrl.SetValue(e)
		
# ############################################################
class RosterTreeCtrl(wx.TreeCtrl) :
	ID_CHAT       = wx.NewId() 
        ID_GROUPCHAT  = wx.NewId()    
        ID_SEND_FILE  = wx.NewId()
        ID_CHECK_OFFLINE = wx.NewId()
        ID_BROADCAST  = wx.NewId()
        
        ID_ADD        = wx.NewId()  
        ID_REMOVE     = wx.NewId()
        ID_MOVE       = wx.NewId()
        ID_COPY       = wx.NewId()
        ID_RENAME     = wx.NewId()
        ID_DETAIL     = wx.NewId()
        ID_SEARCH     = wx.NewId()  

	def __init__(self, parent, id, treeIcon, iconDict, pos = wx.DefaultPosition, size = wx.DefaultSize ) :
		wx.TreeCtrl.__init__(self, parent, -1,  pos, size,  style = wx.TR_LINES_AT_ROOT | wx.TR_ROW_LINES | 
				wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS | wx.TR_NO_LINES | wx.SUNKEN_BORDER | wx.TR_EDIT_LABELS)        
           	
		self._iconDict = iconDict
		self._generalGroupNode = None #u'未分组联系人'
		
                #self.Bind(wx.EVT_COMMAND_TREE_BEGIN_DRAG,  , self.)
		#self.Bind(wx.EVT_COMMAND_TREE_END_DRAG,  , self.)
		
                self.Bind(wx.EVT_TREE_ITEM_ACTIVATED,   self.OnItemActivcated) 
		self.Bind(wx.EVT_TREE_STATE_IMAGE_CLICK,  self.OnImageClick) 
		
                self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)
                self.Bind(wx.EVT_TREE_END_LABEL_EDIT,   self.OnEndLabelEdit)
                self.Bind(wx.EVT_TREE_ITEM_MENU,        self.OnTreeItemMenu)
		
		self.SetImageList(treeIcon)
		
		self._hideOffLine  = False
		
		self.init(False)
        
	#----------------------------------------------------------------------------------------------------------#
        def OnTreeItemMenu(self, event) :
                item = event.GetItem()
                if item == None :
                        return
		jid = self.GetPyData(item)
                self.SelectItem(item)
                menu = wx.Menu()
                if jid == None :
                        menu.Append(self.ID_RENAME, u"改名")
                        menu.Append(self.ID_REMOVE, u"删除本组所有联系人")
                        menu.AppendSeparator()
                        menu.Append(self.ID_BROADCAST, u"发送广播消息")
                else :        
                        menu.Append(self.ID_CHAT, u"开始交谈")
                        menu.Append(self.ID_SEND_FILE, u"发送文件...")
                        menu.AppendSeparator()
		        menu.Append(self.ID_RENAME, u"改名")
                        menu.Append(self.ID_MOVE, u"移动到其它组")
                        menu.Append(self.ID_COPY, u"复制到其它组")
                        menu.Append(self.ID_REMOVE, u"删除联系人")
                        menu.AppendSeparator()
			menu.Append(self.ID_DETAIL, u"联系人详情")
   
                self.Bind(wx.EVT_MENU, self.OnCmdChat,     id = self.ID_CHAT)
                self.Bind(wx.EVT_MENU, self.OnCmdSendFile, id = self.ID_SEND_FILE)
                
		self.Bind(wx.EVT_MENU, self.OnRemove,   id = self.ID_REMOVE)
                self.Bind(wx.EVT_MENU, self.OnMove,     id = self.ID_MOVE)
                self.Bind(wx.EVT_MENU, self.OnCopy,     id = self.ID_COPY)
                self.Bind(wx.EVT_MENU, self.OnRename,   id = self.ID_RENAME)
                self.Bind(wx.EVT_MENU, self.OnDetail,   id = self.ID_DETAIL)
                
                self.PopupMenu(menu)
        
        def OnCmdAddRoster(self, event) :
                dlg = RosterAddDialog(self)
                val = dlg.ShowModal()
                if val == wx.ID_OK :
                        nickname = dlg._nickNameTextCtrl.GetValue()
			tojid = dlg._userIDTextCtrl.GetValue()
			group = dlg._userGroupCtrl.GetValue()
                        glob.imclient.addRoster(tojid, nickname, group)                	
                del dlg
                
        def OnCmdChat(self, event) :
		jid = self.getSelectedJID()
		if jid != None :
                        self.GetParent().GetParent()._sessionMgr.activeChatSession(jid)      
                        
        def OnCmdSendFile(self, event) :
		jid = self.getSelectedJID()
		if jid == None :
			return	
		try :
			presence = self.GetParent()._presences[jid]	
		except :
			print "presence not available"
			return
			
		if presence.type == 'unavailable' :
			return
		
		dlg = wx.FileDialog( self, message = u"选择要发送的文件", 
					defaultDir = os.getcwd(), 
					defaultFile = "",
					wildcard = u"任意类型的文件(*.*)|*.*",
					style = wx.OPEN | wx.CHANGE_DIR
				)

		if dlg.ShowModal() == wx.ID_OK:
			file_name = dlg.GetPath()
			dlg.Destroy()	
			new_jid = presence.jid
			
			session = self.GetParent().GetParent()._sessionMgr.activeChatSession(jid)      
                        fsession = glob.imclient.file_transfer_mgr.new_send_session(new_jid, file_name)
			glob.imclient.file_transfer_mgr.send_si_request(fsession)	
			session.appendFileTransferSession(fsession)			
                
        def OnRemove(self, event) :
                jid = self.getSelectedJID()
		if jid != None :
                        glob.imclient.removeRoster(jid)
			
        def OnMove(self, event) :
                pass
        
        def OnCopy(self, event) :
                pass
        
        def OnRename(self, event) :
                sel = self.GetSelection()
                self.EditLabel(sel)
        
        def OnDetail(self, event) :
                jid = self.getSelectedJID()
		if jid != None :
			glob.imclient.getRosterInfo(jid)
		
        def OnBeginLabelEdit(self, event) :
                node = event.GetItem()
                if self.__isGeneralGroupNode(node) :
                        event.Veto()
                else :
                        self.oldName = self.GetItemText(node)
                
        def OnEndLabelEdit(self, event) :
                if event.IsEditCancelled() :
                        return
			
                newName = event.GetLabel()
                node = event.GetItem()
                        
                if self.__isGroupNode(node) :
                        # 联系人组
                        if newName in glob.imclient.roster.get_groups() : 
                                event.Veto()
                                return
                        glob.imclient.renameGroup(self.oldName, newName)        
                else :
                        #单个联系人
                        jid = self.GetPyData(node)
                        glob.imclient.renameRoster(jid, newName)
                #print newName
        
        def OnChangingMyStatus(self, event) :
		id = event.GetId()
		if id == self.ID_ONLINE :
			show = None
			showText = u"在线"
		elif id == self.ID_FREE :
			show = 'chat'
			showText = u"空闲"
		elif id == self.ID_DND :
			show = 'dnd'
			showText = u"忙碌"
		elif id == self.ID_AWAY :
			show = 'away'
			showText = u'离开'
		elif id == self.ID_HIDE :
			show = 'xa'
			showText = u"不可用"
		else :
			print "error!!!"
			return
			
		self._btnChangeStatus.SetLabel(showText)	
		glob.imclient.sendPresence(show) 
		
	#----------------------------------------------------------------------------------------------------------#
       
        def OnItemActivcated(self, event) :
	        node = event.GetItem()
		if not self.__isGroupNode(node) :
                        parent = self.GetParent()
			jid = self.GetItemPyData(node)
                        if jid != None :
                                parent.GetParent()._sessionMgr.activeChatSession(jid)    
				
        def OnImageClick(self, event) :
		print 'onimageclick'
		node = event.GetItem()
		if self.ItemHasChildren(node) :
                        if self.IsExpanded(node) :
                                self.Collapse(node)
                        else :
                                self.Expand(node)
                
        def OnStateImageClick(self, event) :
                print 'status onimageclick'
		if self._selectItem == None :
                        return
                if self.ItemHasChildren(self._selectItem) :
                        if self.IsExpanded(self._selectItem) :
                                self.Collapse(self._selectItem)
                        else :
                                self.Expand(self._selectItem)
				
        #----------------------------------------------------------------------------------------------------------#
	       
        def updateRoster(self, item) :
		try :
                        presence = self.GetParent()._presences[item.jid]
                        img_index = presence.image_index                        
                except :
                        presence = None
                        img_index = self._iconDict['offline']        
                
                if item.name :
                        itemShow = unicode(item.name)
                else :
                        itemShow = item.jid.as_unicode()
                
                if presence :
                        msg = presence.get_show_message()
                        if msg :
                                itemShow += "  -  " + msg
                        
                '''
		try :
			vcard = self.vcards[jid]
		except	:
			vcard = None
		if not vcard :
			#glob.imclient.getRosterInfo(item.jid)
			pass
		else :
			itemShow = vcard.fn.value
		'''	
                #print "roster.updateRoster : name = %s, jid = %s, group = %s" % (itemShow,item.jid,item.groups)
                  
                if item.subscription in ['none'] and item.ask and len(item.groups) == 0 :
                        groups = [OTHER_GROUP_NAME,]
                        
                elif len(item.groups) == 0 and item.subscription == 'both':
                        groups = [GENERAL_GROUP_NAME,]
                else :
                        groups = item.groups[:]
                        
                for groupName in groups :
                        groupNode = self.__findGroupNodeByName(groupName)
                        if not groupNode :
                                groupNode = self.__addRosterGroupNode(groupName)
                        childNode = self.__findRosterOfGroup(groupNode, item.jid)
                        if not childNode :
                                childNode = self.AppendItem(groupNode, itemShow)
                                self.SetPyData(childNode, item.jid)
                        #self.EnsureVisible(childNode)
			self.SetItemImage(childNode, img_index)
                        self.SetItemText(childNode, itemShow)
                        self.ExpandAllChildren(groupNode)
                
                #clear old nodes
                nodes = self.__findNodesByJid(item.jid) 
                for node in nodes :
                        parentname = self.GetItemText(self.GetItemParent(node))
                        if parentname not in groups :
                                self.Delete(node)
                        elif self._hideOffLine and not self.__isOnLine(item.jid):
                                self.Delete(node)
                                
                #clear empty groups
                (groupNode,cookie) = self.GetFirstChild(self.RootItem)
                while groupNode.IsOk(): 
                        if (self.GetChildrenCount(groupNode) == 0) \
				and (self.GetItemText(groupNode) != GENERAL_GROUP_NAME):
                                self.Delete(groupNode)
                        (groupNode,cookie) = self.GetNextChild(self.RootItem, cookie)
                #self.ExpandAllChildren(self.RootItem)        
                
        def init(self, connected = True) :
                self.DeleteAllItems()
		self.generalGroupNode = None
		
		if connected :
			self.AddRoot("ContactsList")
			self.generalGroupNode = self.__addRosterGroupNode(GENERAL_GROUP_NAME)
        
	def getSelectedJID(self) :
		node =self.GetSelection()
		
		if node == None :
			return None
			
		jid = self.GetItemPyData(node)

		return jid
		
	def hideOffLine(self, hide) :
		self._hideOffLine = hide
        
	def  __deleteRoster(self, jid) :
                groups = []
                (groupNode,cookie) = self.GetFirstChild(self.RootItem)
		#find all groups to variable groups
                while groupNode.IsOk(): 
                        groups.append(groupNode) 
                        (groupNode,cookie) = self._GetNextChild(self.RootItem, cookie)
                
                for node in groups :     
                        (childNode, cookie) = self.GetFirstChild(node)
                        while childNode.IsOk(): 
                                data = self.GetPyData(childNode)
                                if data == jid :
                                        self.Delete(childNode)
                                (childNode, cookie) = self.GetNextChild(node, cookie)
                        #end while                        
                #end for  
		
	def __findGroupNodeByName(self, groupName) :
                groupNode,cookie = self.GetFirstChild(self.RootItem)
                while groupNode: 
                        if self.GetItemText(groupNode) == groupName :
                                return groupNode
                        else :
                                groupNode,cookie = self.GetNextChild(self.RootItem, cookie)
                return None
        
	
        def __findRosterOfGroup(self, groupNode, jid) :
                node,cookie = self.GetFirstChild(groupNode)
                while node: 
                        if self.GetPyData(node) == jid :
                                return node
                        else :
                                node,cookie = self.GetNextChild(groupNode, cookie)
                return None
                
        def __findNodesByJid(self, jid) :
                nodes = []
                groupNode,cookie = self.GetFirstChild(self.RootItem)
                while groupNode: 
                        node,cookie2 = self.GetFirstChild(groupNode)
                        while node: 
                                if self.GetPyData(node) == jid :
                                        nodes.append(node)
                                node,cookie2 = self.GetNextChild(groupNode, cookie2)
                        
                        groupNode,cookie = self.GetNextChild(self.RootItem, cookie)
                return nodes
        	
        def __isGroupNode(self, node) :
                return (self.GetItemParent(node) == self.RootItem)
                
        def __isGeneralGroupNode(self, node) :
               return node == self.generalGroupNode
	
        def __addRosterGroupNode(self, groupName) :        
                groupNode = self.AppendItem(self.RootItem, groupName)
             
                self.SetItemImage(groupNode, self._iconDict['groupclose'], wx.TreeItemIcon_Normal)
                self.SetItemImage(groupNode, self._iconDict['groupopen'], wx.TreeItemIcon_Expanded)
		
                return groupNode
        
	def __isOnLine(self, jid) :
		try :
                        presence = self.GetParent()._presences[jid]
			if presence.type != 'unavailable' :
				return True
                        else :
                                return False
                except:
                        return False
                
               
# ############################################################   
	
class RosterPanel(wx.Panel) :
        ID_CONNECT     = wx.NewId()  
        ID_DISCONNECT  = wx.NewId()  

        ID_CHAT       = wx.NewId() 
        ID_GROUPCHAT  = wx.NewId()    
        ID_SEND_FILE  = wx.NewId()
        ID_BROADCAST  = wx.NewId()
        ID_CHECK_OFFLINE = wx.NewId()
	ID_PERSONAL_INFO = wx.NewId() 
        
        ID_ADD        = wx.NewId()  
        ID_REMOVE     = wx.NewId()
        ID_MOVE       = wx.NewId()
        ID_COPY       = wx.NewId()
        ID_RENAME     = wx.NewId()
        ID_DETAIL     = wx.NewId()
        ID_SEARCH     = wx.NewId()  

	ID_ONLINE     = wx.NewId() 
	ID_FREE       = wx.NewId() 
	ID_DND        = wx.NewId() 
	ID_HIDE       = wx.NewId() 
	ID_AWAY      = wx.NewId() 
	
        def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize) :
                wx.Panel.__init__(self, parent, -1, pos, size)
                
                sizer = wx.BoxSizer(wx.VERTICAL)
                
                self._actions = self.MakeActions()    
                self._toolBar = self.MakeToolBar()
		
                sizer.Add(self._toolBar, 0, wx.ALIGN_TOP|wx.ALL, 2)
		
                self._iconIndex = {}
                self._treeIcon = wx.ImageList(16, 16)
                iconlist = ['groupopen', 'groupclose', 
                            'online', 'offline',
                            'chat', 'dnd', 'away', 'xa', 
                            'ask', 'noauth'
                            ]
                for item in iconlist :
                        self._iconIndex[item] = self._treeIcon.Add(glob.getBitmap(item))
                
                self._rosterCtrl = RosterTreeCtrl(self, -1, self._treeIcon, self._iconIndex)        
	
		sizer.Add(self._rosterCtrl, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 1)
	  
                #self.Bind(wx.EVT_COMMAND_TREE_BEGIN_DRAG,  , self._rosterCtrl)
		#self.Bind(wx.EVT_COMMAND_TREE_END_DRAG,  , self._rosterCtrl)
		
                self._btnChangeStatus = wx.Button(self, -1, u'')
		self._btnChangeStatus.Enable(False)
                self.Bind(wx.EVT_BUTTON, self.OnBtnChangeStatus, self._btnChangeStatus)
                sizer.Add(self._btnChangeStatus, 0, wx.ALIGN_BOTTOM | wx.ALL |wx.EXPAND, 1)
       	        
                self.SetSizer(sizer)
                #sizer.Fit(self)
                
                #self.Bind(imclient.EVT_IM_PRESENCE_UPDATE,  self.OnPresenceUpdate)
		#self.Bind(imclient.EVT_IM_ROSTER_UPDATE,    self.OnRosterUpdate)
                
                self.Bind(wx.EVT_TOOL, self.OnCmdAddRoster,  id = self.ID_ADD)
                self.Bind(wx.EVT_TOOL, self.OnCmdHideOffline,  id = self.ID_CHECK_OFFLINE)
                '''
                self.Bind(wx.EVT_MENU, self.OnChat,     id = self.ID_CHAT)
                self.Bind(wx.EVT_MENU, self.OnSendFile, id = self.ID_SEND_FILE)
                
		self.Bind(wx.EVT_MENU, self.OnRemove,   id = self.ID_REMOVE)
                self.Bind(wx.EVT_MENU, self.OnMove,     id = self.ID_MOVE)
                self.Bind(wx.EVT_MENU, self.OnCopy,     id = self.ID_COPY)
                self.Bind(wx.EVT_MENU, self.OnRename,   id = self.ID_RENAME)
                self.Bind(wx.EVT_MENU, self.OnDetail,   id = self.ID_DETAIL)
                '''
		self.Bind(wx.EVT_MENU, self.OnChangingMyStatus, id = self.ID_ONLINE)
		self.Bind(wx.EVT_MENU, self.OnChangingMyStatus, id = self.ID_FREE)
		self.Bind(wx.EVT_MENU, self.OnChangingMyStatus, id = self.ID_DND)
		self.Bind(wx.EVT_MENU, self.OnChangingMyStatus, id = self.ID_AWAY)
		self.Bind(wx.EVT_MENU, self.OnChangingMyStatus, id = self.ID_HIDE)
                
                self._presences = PresenceStatus(self, self._iconIndex)
                
                self._vcards = {} 
	
	#----------------------------------------------------------------------------------------------------------#
        def MakeActions(self) :
                act = actions.Actions(self)
                
                act.AddAction(self.ID_ADD, 
                                u"添加联系人", 
                                glob.getBitmap('add'),  
                                self.OnCmdAddRoster
                                )
				
                act.AddAction(self.ID_GROUPCHAT, 
                                u"群聊", 
                                glob.getBitmap('groupchat'), 
                                None
                                )

                act.AddAction(self.ID_SEND_FILE, 
                                u"发送文件", 
                                glob.getBitmap('filetransfer'), 
                                self.OnCmdSendFile,
                                )
                
		act.AddAction(self.ID_PERSONAL_INFO, 
                                u"个人信息", 
                                glob.getBitmap('self'),
                                self.OnCmdPersonalInfo
                                )
                               
		act.AddCheckAction(self.ID_CHECK_OFFLINE, 
                                u"显示离线联系人", 
                                glob.getBitmap('offline'), 
                                self.OnCmdHideOffline, checked = True
                                )
				
                #act.AddAction( ,)
                #act.AddAction( ,)
                #act.AddAction( ,)
                
                return act
                
        def MakeToolBar(self) :
                tb = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
                tb.SetToolBitmapSize(wx.Size(16,16))
                
                self._actions[self.ID_ADD].AppendToToolBar(tb)
                self._actions[self.ID_GROUPCHAT].AppendToToolBar(tb)
                #self._actions[self.ID_SEND_FILE].AppendToToolBar(tb)
                tb.AddSeparator()
		
		self._actions[self.ID_PERSONAL_INFO].AppendToToolBar(tb)
		tb.AddSeparator()
		
                self._actions[self.ID_CHECK_OFFLINE].AppendToToolBar(tb)
                '''
		tbtn = platebtn.PlateButton(tb, wx.ID_ANY, u' 连接 ', glob.getBitmap('connect'), style = platebtn.PB_STYLE_SQUARE)
		menu = wx.Menu()
		menu.Append(wx.NewId(), u"上线")
		menu.Append(wx.NewId(), u"离线")
		tbtn.SetMenu(menu)
        
		tb.AddControl(tbtn)
		'''
		
                tb.Realize()
                return tb
                
        #----------------------------------------------------------------------------------------------------------#
        
        def OnCmdHideOffline(self, event) :
                self._actions[self.ID_CHECK_OFFLINE].CheckReverse()  
		self._rosterCtrl.hideOffLine(not self._actions[self.ID_CHECK_OFFLINE].checked)
		
		if not glob.imclient.roster :
			return 
	
                for item in glob.imclient.roster.get_items():
                        self._rosterCtrl.updateRoster(item)
                
        def OnRosterUpdate(self, event) :
                item = event.rosterItem
		
                if item != None :
                        self._rosterCtrl.updateRoster(item)
                else :
                        self._rosterCtrl.init()  
                        for item in glob.imclient.roster.get_items() :
				self._rosterCtrl.updateRoster(item)
				
        def OnCmdAddRoster(self, event) :
                dlg = RosterAddDialog(self)
                val = dlg.ShowModal()
                if val == wx.ID_OK :
                        nickname = dlg._nickNameTextCtrl.GetValue()
			tojid = dlg._userIDTextCtrl.GetValue()
			group = dlg._userGroupCtrl.GetValue()
                        glob.imclient.addRoster(tojid, nickname, group)                	
                del dlg
                                
        def OnCmdSendFile(self, event) :
                pass
        
	def OnCmdPersonalInfo(self, event) :
		dlg = MyInfoDialog(None)
		dlg.ShowVcard(None)
                	
        def OnChangingMyStatus(self, event) :
		id = event.GetId()
		if id == self.ID_ONLINE :
			show = None
			showText = u"在线"
		elif id == self.ID_FREE :
			show = 'chat'
			showText = u"空闲"
		elif id == self.ID_DND :
			show = 'dnd'
			showText = u"忙碌"
		elif id == self.ID_AWAY :
			show = 'away'
			showText = u'离开'
		elif id == self.ID_HIDE :
			show = 'xa'
			showText = u"不可用"
		else :
			print "error!!!"
			return
			
		self._btnChangeStatus.SetLabel(showText)	
		glob.imclient.sendPresence(show) 
		
	def OnBtnChangeStatus(self, event) :
		menu = wx.Menu()
	        # Show how to put an icon in the menu
	        item = wx.MenuItem(menu, self.ID_ONLINE, u"在线")
	        #bmp = images.getSmilesBitmap()
	        #item.SetBitmap(bmp)
	        menu.AppendItem(item)
	        # add some other items
	        menu.Append(self.ID_FREE,  u"空闲")
	        menu.Append(self.ID_DND,   u"忙碌")
	        menu.Append(self.ID_AWAY, u"离开")
	        menu.Append(self.ID_HIDE,  u"不可用")
		self.PopupMenu(menu)
		#menu.Destroy()
	
        #----------------------------------------------------------------------------------------------------------#
        
        def OnPresenceUpdate(self, event) :
                status = self._presences.AddPresenceStatus(event.stanza)
                
		if status.jid == glob.imclient.jid:
			self.OnChangedMyStatus(status)	
			
		elif  status.jid.bare() != glob.imclient.jid.bare() :		
                        try :
                                item = glob.imclient.roster[status.jid.bare()]
                                self._rosterCtrl.updateRoster(item) 
                        except Exception, e:
                                print "error in OnPresenceUpdate : ", e
				print "JID : ", status.jid.as_unicode()
				pass
                
	def OnVcardUpdate(self, event) :
		if event.result == False :
			return	
		stanza = event.stanza
		jid = stanza.get_from()	
		try:
			node=stanza.get_query()
			if node:
				vcard=VCard(node)
			else:
				vcard=None
		except (ValueError,),e:
			vcard=None
		if vcard is None:
			#self.error(u"Invalid vCard received from "+stanza.get_from().as_unicode())
			return
			
		self._vcards[jid] = vcard
		
		try :
			itemShow = vcard.nickname[0].value
		except :
			itemShow = ''
			
		if itemShow == '' :	
			try :
				itemShow = vcard.fn.value
			except :
				itemShow = ''
		
		if itemShow == '' :
			return
		
		print itemShow
		
		#nodes = self._rosterCtrl.findNodesByJid(jid)
		#for node in nodes :
		#	self._rosterCtrl.SetItemText(node, itemShow)
		
	def OnChangedMyStatus(self, presence) :
		msg = presence.get_show_message()
		self._btnChangeStatus.SetLabel(unicode(msg))
	
        #----------------------------------------------------------------------------------------------------------#
        
	def notifyOnline(self) :
		self._rosterCtrl.init(True)
		self._btnChangeStatus.Enable(True)
		self._btnChangeStatus.SetLabel(u'在线')
	
	def notifyOffline(self) :
		self._btnChangeStatus.Enable(False)
		self._btnChangeStatus.SetLabel('')
		self._rosterCtrl.init(False)
		
        #----------------------------------------------------------------------------------------------------------#
             
# ############################################################                        