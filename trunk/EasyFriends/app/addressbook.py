
# -*- coding: utf-8 -*-

import os, sys, math
import wx
import wx.lib.mixins.listctrl  as  listmix
import  wx.grid  as  gridlib

import libxml2

from glob import glob
import event, imclient, actions, storage,util

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient

# ############################################################       
class ContactItem :
	def __init__(self, name = '', phone = '', email = '', address = '', other_info = '') :
		self.name = name
		self.phone = phone
		self.email = email
		self.address = address
		self.other_info = other_info
	
	def to_xml(self) :
		return "<name>%s</name><phone>%s</phone><email>%s</email><address>%s</address><other>%s</other>" % (self.name.encode('utf-8'), self.phone.encode('utf-8'), self.email.encode('utf-8'), self.address.encode('utf-8'), self.other_info.encode('utf-8'))
 	
	def from_xml(self, xml) :
		pass	
	
# ############################################################       
class AddressBookStorage(storage.StorageItem) :
	def __init__(self, storage_mgr = None) :
		storage.StorageItem.__init__(self, 'myspace:addressbook', 'phone_book', storage_mgr)
		self.addr_list = []
		
	def add_item(self,  name = '', phone = '', email = '', address = '', other_info = '') :	
		item = ContactItem(name, phone, email, address, other_info)
		self.addr_list.append(item)
		return item
	
	def unload(self) :
		self.addr_list = []
		storage.StorageItem.unload(self)
		
	def to_xml(self) :
		str = ''
		for item in self.addr_list :
			str = str + '<line>' + item.to_xml() + '</line>'	
		return str
		
	def from_xml(self, data) :
		try :
			doc = '<?xml version="1.0" encoding="UTF-8"?>\n<data>' + data + '</data>'	
			root = libxml2.parseDoc(doc)
			line = root.children.children
			while line :
				name = ''
				phone = ''
				email = ''
				address = ''
				other_info = ''
				item = line.children
				while item :
					if item.name == 'name' :
						name = item.getContent().decode('utf-8')
					elif item.name == 'phone' :
						phone = item.getContent().decode('utf-8')
					elif item.name == 'email' :
						email = item.getContent().decode('utf-8')
					elif item.name == 'address' :
						address = item.getContent().decode('utf-8')	
					elif item.name == 'other' :
						other_info = item.getContent().decode('utf-8')	
					item = item.next
				#end of while item	
				self.add_item(name, phone, email, address, other_info) 
				line = line.next
			#end of while line	
			#self.ShowAddressBook()
		except Exception, e :
			print "error in from_xml : ", str(e)
				
				
glob.register_storage(AddressBookStorage())

# ############################################################       
class AddressBookListCtrl(wx.ListCtrl, listmix.TextEditMixin):
	def __init__(self, parent, book, ID = -1,  style = wx.LC_REPORT | wx.LC_VIRTUAL):
	        wx.ListCtrl.__init__(self, parent, ID, wx.DefaultPosition, wx.DefaultSize, style)
	   
		#listmix.ListCtrlSelectionManagerMix.__init__(self)
	        
		self.addressbook = book 
		
		self.InsertColumn(0, u"姓名")
                self.SetColumnWidth(0, 100)
                self.InsertColumn(1, u"电话")
                self.SetColumnWidth(1, 100)
                self.InsertColumn(2, u"电子邮件")
                self.SetColumnWidth(2, 150)
                self.InsertColumn(3, u"联系地址")
                self.SetColumnWidth(3, 150)
                self.InsertColumn(4, u"其他")
                self.SetColumnWidth(4, 250)
	
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		
		listmix.TextEditMixin.__init__(self)	
		
	        self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("light gray")
		
		self.currentItem = -1
		
	def OnItemSelected(self, event):
		self.currentItem = event.m_itemIndex
		listmix.TextEditMixin.OnItemSelected(self, event)
		
	def OnItemActivated(self, event):
		self.currentItem = event.m_itemIndex
		
	def OnItemDeselected(self, evt):
		self.currentItem = -1
		#self.log.WriteText("OnItemDeselected: %s" % evt.m_itemIndex)

        #def getColumnText(self, index, col):
	#	item = self.GetItem(index, col)
	#	return item.GetText()

	def OnGetItemText(self, row, col):
		item = self.addressbook.addr_list[row]
		if col == 0:
			return item.name
		elif col == 1 :
			return item.phone
		elif col == 2 :
			return item.email
		elif col == 3 :
			return item.address
		elif col == 4 :
			return item.other_info

	def SetVirtualData(self, row, col, text) :
		item = self.addressbook.addr_list[row]
		if col == 0:
			item.name = text
		elif col == 1 :
			item.phone = text
		elif col == 2 :
			item.email = text
		elif col == 3 :
			item.address = text
		elif col == 4 :
			item.other_info = text

	def OnGetItemImage(self, item):
		return -1
		if item % 3 == 0:
			return self.idx1
		else:
			return -1

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr1
		else:
			return None

	def UpdateData(self) :
		self.SetItemCount(len(self.addressbook.addr_list))
		self.Refresh()
		
# ############################################################       	
class AddressBookPanel(wx.Panel, storage.StorageItemMonitor) :
	ID_IMPORT   = wx.NewId()
	ID_EXPORT   = wx.NewId()
	ID_ADD_ITEM = wx.NewId()
	ID_DEL_ITEM = wx.NewId()
	ID_SAVE     = wx.NewId()
	
        def __init__(self, parent, id = -1, ) :
                wx.Panel.__init__(self, parent, id, pos = wx.DefaultPosition, size = wx.DefaultSize)
                
		sizer = wx.BoxSizer(wx.VERTICAL)
		
                self._actions = self.MakeActions()    
                self._toolBar = self.MakeToolBar()
		
                sizer.Add(self._toolBar, 0, wx.ALIGN_TOP|wx.ALL, 2)
		
		self.addr_book = glob.storages['phone_book']
		self.addr_book.set_monitor(self)
		
		self._addrListCtrl = AddressBookListCtrl(self, self.addr_book)
                
		sizer.Add(self._addrListCtrl, 1, wx.EXPAND|wx.ALIGN_CENTER, 0)
		
		self.SetSizer(sizer)
                
	def MakeActions(self) :
                act = actions.Actions(self)
                
                act.AddAction(self.ID_IMPORT, 
                                u"导入", 
                                glob.getBitmap('import'),  
                                self.OnCmdImport
                                )
		
		act.AddAction(self.ID_EXPORT, 
                                u"导出", 
                                glob.getBitmap('export'),  
                                self.OnCmdExport
                                )
		
		act.AddAction(self.ID_ADD_ITEM, 
                                u"添加", 
                                glob.getBitmap('add'),  
                                self.OnCmdAddItem
                                )
		
		act.AddAction(self.ID_DEL_ITEM, 
                                u"删除", 
                                glob.getBitmap('remove'),  
                                self.OnCmdDelItem
                                )
		
		act.AddAction(self.ID_SAVE, 
                                u"保存", 
                                glob.getBitmap('save'),  
                                self.OnCmdSave
                                )
		
		return act
		
	def MakeToolBar(self) :
                tb = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
                tb.SetToolBitmapSize(wx.Size(16,16))
                
                self._actions[self.ID_ADD_ITEM].AppendToToolBar(tb)
                self._actions[self.ID_DEL_ITEM].AppendToToolBar(tb)
                self._actions[self.ID_SAVE].AppendToToolBar(tb)
                tb.AddSeparator()
		self._actions[self.ID_IMPORT].AppendToToolBar(tb)
                self._actions[self.ID_EXPORT].AppendToToolBar(tb)
                
                tb.Realize()
                
                return tb
		
	def ShowAddressBook(self) :
		self._addrListCtrl.UpdateData()
		
	def OnCmdAddItem(self, event) :
		self.addr_book.add_item(u":请输入联系人姓名:")
		self._addrListCtrl.UpdateData()
		index = len(self.addr_book.addr_list) - 1
		self._addrListCtrl.EnsureVisible(index)
		#self._addrListCtrl.
		
	def OnCmdDelItem(self, event) :
		if self._addrListCtrl.currentItem >= 0 :
			del self.addr_book.addr_list[self._addrListCtrl.currentItem]
			self._addrListCtrl.UpdateData()
	
	def OnCmdImport(self, event) :
		#TODO
		pass
	
	def OnCmdExport(self, event) :
		#TODO
		pass
	
	def OnCmdSave(self, event) :
		self.addr_book.save()
	
	def ShowAddressBook(self) :
		self._addrListCtrl.UpdateData()
	
	def on_load(self, isok) :
		self.ShowAddressBook()
		
	def on_unload(self) :
		self.ShowAddressBook()
		
	def on_save(self, isok) :
		hint = util.MessageHint(self) 
		hint.Msg(u"    数据保存成功!    ")
		#sizer = self.GetSizer()
		#label = wx.StaticText(self, -1, u"数据保存成功")
		#sizer.Add(label, 0, wx.EXPAND | wx.ALIGN_BOTTOM, 0)
		
# ############################################################                

