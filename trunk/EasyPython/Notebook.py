#coding:utf-8

import os.path

import wx
import wx.lib.agw.aui as aui

import wx.stc
from drText import DrText
import drEncoding

import config, glob, utils

#*******************************************************************************************************
class DocNotebook(aui.AuiNotebook):
    def __init__(self, parent):
        
        notebook_style = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE #| wx.NO_BORDER
        
        aui.AuiNotebook.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, notebook_style)
        
        images = [  
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/unmodified.png", wx.BITMAP_TYPE_PNG)),
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/modified.png", wx.BITMAP_TYPE_PNG)),
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/active_unmodified.png", wx.BITMAP_TYPE_PNG)),
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/active_modified.png", wx.BITMAP_TYPE_PNG))
                ]

        self.imagelist = wx.ImageList(16, 16)
        self.images = images
        map(self.imagelist.Add, self.images)
        self.AssignImageList(self.imagelist)
      
        arts = [aui.AuiDefaultTabArt, aui.AuiSimpleTabArt, aui.VC71TabArt, aui.FF2TabArt,
                aui.VC8TabArt, aui.ChromeTabArt]
        art = arts[5]()
        self.SetArtProvider(art)
      
    def SetDocManager(self, docMgr) :
        self.docMgr = docMgr
        
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClosing)
        #self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.OnPageClosed)
        
        self.Bind( wx.EVT_RIGHT_DOWN,            self.OnPopUp )
        #self.Bind( wx.EVT_LEFT_UP,               self.OnSelectTab )
        #self.Bind( wx.EVT_LEFT_DCLICK,           self.OnLeftDoubleClick )
        
    def OnPageChanged(self, event):
        index = event.GetSelection()
        self.docMgr.SelectDoc(index)
    
    def OnPageClosing(self, event):
        glob.MainFrame.OnCloseFile(None)
    
    def OnPageClosed(self, event):
        count = self.GetPageCount()
        if count == 0:
              self.docMgr.SelectDoc(-1)
        
    def OnPopUp(self, event):
        tabmenu = wx.Menu()
        tabmenu.Append(glob.MainFrame.ID_CLOSE, u"关闭(&Close)")
        tabmenu.Append(glob.MainFrame.ID_CLOSE_ALL, u"关闭所有页面(Close &All Tabs)")
        tabmenu.Append(glob.MainFrame.ID_CLOSE_ALL_OTHER_DOCUMENTS, u"关闭其他所有页面(Close All &Other Tabs)")
        tabmenu.AppendSeparator()
        tabmenu.Append(glob.MainFrame.ID_SAVE, u"保存(&Save)")
        tabmenu.Append(glob.MainFrame.ID_SAVE_AS, u"另存为(Save &As)...")

        ht = self.HitTest(event.GetPosition())[0]
        if ht > -1:
            self.SetSelection(ht)

        self.PopupMenu(tabmenu, event.GetPosition())
        
        #tabmenu.Destroy()