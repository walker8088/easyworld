
# -*- coding: utf-8 -*-

import os, math, base64
import wx

from glob import glob
import util

import event, imclient, actions

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient

import storage, actions

# ############################################################ 
class NoteBookStorage(storage.StorageItem) :
	def __init__(self, storage_mgr = None) :
		storage.StorageItem.__init__(self, 'myspace:notebook', 'note_book', storage_mgr)
		self.text = ''
			
	def from_xml(self, data) :
		self.text = base64.b64decode(data).decode('utf-8')
		
	def to_xml(self) :	
		dtext = base64.b64encode(self.text.encode('utf-8'))
		return dtext
		
glob.register_storage(NoteBookStorage())
		
# ############################################################ 
class NoteBookPanel(wx.Panel, storage.StorageItemMonitor) :
	ID_SAVE = wx.NewId()
	ID_CANCEL = wx.NewId()
	
        def __init__(self, parent) :
                wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)
                
		sizer = wx.BoxSizer(wx.VERTICAL)
                
		self._actions = self.MakeActions()    
		self._toolBar = self.MakeToolBar()
		
		sizer.Add(self._toolBar, 0, wx.ALIGN_TOP, 0)
		
		self._editCtrl = wx.TextCtrl(self, -1, "", style = wx.TE_MULTILINE | wx.TE_RICH2)
		sizer.Add(self._editCtrl, 1, wx.EXPAND | wx.ALIGN_CENTER, 0)
		
		self.SetSizer(sizer)
		
		self.storage = glob.storages['note_book'] 
		
		self.storage.set_monitor(self)
		
		self._editCtrl.SetValue(self.storage.text)
		
	def MakeActions(self) :
                act = actions.Actions(self)
                
                act.AddAction(self.ID_SAVE, 
                                u"保存", 
                                glob.getBitmap('save'),  
                                self.OnCmdSave
                                )
		return act
		
	def MakeToolBar(self) :
                tb = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
                tb.SetToolBitmapSize(wx.Size(16,16))
                
                self._actions[self.ID_SAVE].AppendToToolBar(tb)
                
                tb.Realize()
                
                return tb
		
	def OnCmdSave(self, evt) :
		self.storage.text = self._editCtrl.GetValue()
		self.storage.save()
	
	def on_load(self, isok) :
		self._editCtrl.SetValue(self.storage.text)
		self.Refresh()
		
	def on_save(self, isok) :
		hint = util.MessageHint(self) 
		hint.Msg(u"    数据保存成功!    ")
		#sizer = self.GetSizer()
		#label = wx.StaticText(self, -1, u"数据保存成功")
		#sizer.Add(label, 0, wx.EXPAND | wx.ALIGN_BOTTOM, 0)
		
# ############################################################                
	