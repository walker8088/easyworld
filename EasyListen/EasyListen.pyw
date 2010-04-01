#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path, sys, threading, time, socket
import string, sets, struct, Queue

import wx, wx.html, wx.media
from wx.lib.ticker import Ticker

import lrcParser

APP_NAME    = 'Easy Study'
APP_VERSION = 'Version 0.1 Pre'
ICON_NAME   = 'EasyStudy.ico'

class MyTaskBarIcon(wx.TaskBarIcon):	
	ID_MenuExit = wx.NewId()

	def __init__(self, frame, icon):
		wx.TaskBarIcon.__init__(self)	
                
		self.frame = frame	
                self.icon  = icon
                
		self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnTaskBarClick)
                self.Bind(wx.EVT_MENU, self.OnMenuExit, id=self.ID_MenuExit)

        def ShowIcon(self, yes = True) :
                if yes :
                        self.SetIcon(self.icon, APP_NAME)
		elif self.IsIconInstalled():
                        self.RemoveIcon() 
        #override	
        def CreatePopupMenu(self):
		menu = wx.Menu()		
                menu.Append(self.ID_MenuExit, '&Exit')
                return menu
                
	def OnTaskBarClick(self, event):
		if self.frame.IsIconized():
                        self.frame.Iconize(False)
                if not self.frame.IsShown():
			self.frame.Show(True)
		self.frame.Raise()
                self.ShowIcon(False)
        
        def OnMenuExit(self, event):
		self.frame.Close()
                

# The wx.VListBox is much like a regular wx.ListBox except you draw the
# items yourself and the items can vary in height.
class MyVListBox(wx.VListBox):

    # This method must be overridden.  When called it should draw the
    # n'th item on the dc within the rect.  How it is drawn, and what
    # is drawn is entirely up to you.
    def OnDrawItem(self, dc, rect, n):
        if self.GetSelection() == n:
            c = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        else:
            c = self.GetForegroundColour()
        dc.SetFont(self.GetFont())
        dc.SetTextForeground(c)
        dc.DrawLabel(self._getItemText(n), rect,
                     wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

    # This method must be overridden.  It should return the height
    # required to draw the n'th item.
    def OnMeasureItem(self, n):
        height = 0
        for line in self._getItemText(n).split('\n'):
            w, h = self.GetTextExtent(line)
            height += h
        return height + 5


    # These are also overridable:
    #
    # OnDrawSeparator(dc, rect, n)
    #   Draw a separator between items.  Note that rect may be reduced
    #   in size if desired so OnDrawItem gets a smaller rect.
    #
    # OnDrawBackground(dc, rect, n)
    #   Draw the background and maybe a border if desired.


    def _getItemText(self, item):
        if item % 2 == 0:
            return "This is item# %d" % item
        else:
            return "This is item# %d\n with an extra line" % item

            
                
class MyHtmlListBox(wx.HtmlListBox):
        #def __init__(self, parent, id, size, style) :
        #        wx.HtmlListBox.__init__(self, parent, id, size, style)
        
        def SetTagValue(self, t):
                self.tagValue = t
                self.currentIndex = -1
                if t == None:
                        self.SetItemCount(0) 
                else:
                        self.SetItemCount(len(self.tagValue[0])) 
                        self.SetSelection(-1)
                
        def OnGetItem(self, n):
                #return self.tagValue[1][n]
                #print 'getItem', n
                if n == self.currentIndex:
                        return "<h3><font color='RED'>" + self.tagValue[1][n].decode('cp936') + '</font></h3>'
                else :
                        return "<h5>" + self.tagValue[1][n].decode('cp936') + '</h5>'
                        
        def MarkCurrentShow(self, markms) :
                if self.tagValue == None:
                        return
                #last line
                if self.currentIndex == len(self.tagValue[0]) -1 and markms >= self.tagValue[0][self.currentIndex]:
                        return
                        
                newIndex = self.currentIndex
                #new selection   or  forward       
                if self.currentIndex == -1  or markms > self.tagValue[0][self.currentIndex] :        
                        for msitem in self.tagValue[0][newIndex + 1:] :
                                if markms >= msitem :
                                        newIndex += 1
                                else :
                                        break
                #backward
                elif markms < self.tagValue[0][self.currentIndex] :
                        newIndex = 0
                        for msitem in self.tagValue[0][:self.currentIndex] :
                                if markms >= msitem :
                                        newIndex += 1
                                        #print newIndex
                                else :
                                        break
                                        
                if self.currentIndex == newIndex :
                        return
                self.currentIndex = newIndex
                self.SetSelection(self.currentIndex)
                middleShowIndex = int((self.GetVisibleBegin() + self.GetVisibleEnd()) / 2)
                if self.currentIndex > middleShowIndex or self.currentIndex < self.GetVisibleBegin():
                        self.ScrollLines(self.currentIndex - middleShowIndex)
                self.RefreshAll()
                
                #sequence move        
                #for i in range(len(self.tagValue[0]) -1) :
                #      msbegin = self.tagValue[0][i]
                #      msend = self.tagValue[0][i + 1]
                #      if ms >= msbegin and ms <= msend :
                #                if self.currentIndex != i :
                #                        self.currentIndex = i
                #                        self.SetSelection(self.currentIndex)
                #                        middleShowIndex = int((self.GetVisibleBegin() + self.GetVisibleEnd()) / 2)
                #                        if self.currentIndex > middleShowIndex or self.currentIndex < self.GetVisibleBegin():
                #                                self.ScrollLines(self.currentIndex - middleShowIndex)
                #                        self.RefreshAll()
                #                       #print self.currentIndex
                #                break
                #end for
   
# ############################################################  	
class SliceRecord :
	def __init__(self, start = None, stop = None, contents = '') :
		self.start = start
		self.stop  = stop
		self.contents = contents
		
# ############################################################  	
class SliceVirtualList(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, 
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES
			)
			
	        self.InsertColumn(0, u"序号")
	        self.InsertColumn(1, u"开始")
	        self.InsertColumn(2, u"结束")
	        self.InsertColumn(3, u"内容")
	        self.SetColumnWidth(0, 50)
	        self.SetColumnWidth(1, 70)
	        self.SetColumnWidth(2, 50)
	        self.SetColumnWidth(3, 250)

	        self.SetItemCount(0)
		self.data = []
		
	        self.attr1 = wx.ListItemAttr()
	        self.attr1.SetBackgroundColour("yellow")

	        self.attr2 = wx.ListItemAttr()
	        self.attr2.SetBackgroundColour("light blue")

	        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
	        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
	        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

	def OnItemSelected(self, event):
		self.currentItem = event.m_itemIndex
     
	def OnItemActivated(self, event):
		self.currentItem = event.m_itemIndex
        
	def OnItemDeselected(self, evt):
		#self.log.WriteText("OnItemDeselected: %s" % evt.m_itemIndex)
		pass
	
	def OnGetItemText(self, item, col):
	        value  = self.data[item]
		if col == 0 :
			return str(item + 1)
		else :
			return value[col]
			
	def OnGetItemAttr(self, item):
	        if item % 3 == 1:
	            return self.attr1
	        elif item % 3 == 2:
	            return self.attr2
	        else:
	            return None
	    
	def appendData(self, tag_log) :
		self.data.append(tag_log)
		self.SetItemCount(len(self.data))
	        self.Refresh()
		
	def clearData(self) :
		self.data = []
		self.SetItemCount(len(self.data))
	        self.EnsureVisible(self.ItemCount-1)
		self.Refresh()
		
	def getColumnText(self, index, col):
	        item = self.GetItem(index, col)
	        return item.GetText()
		
# ############################################################  	
class MainFrame(wx.Frame):   
        def __init__(self, parent = None, id=-1, title = APP_NAME, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | wx.CLIP_CHILDREN):

                wx.Frame.__init__(self, parent, id, title, pos, size, style)
                
                icon = wx.Icon(ICON_NAME, wx.BITMAP_TYPE_ICO)
        	self.SetIcon(icon)
        	
                self.statusBar = self.CreateStatusBar(1, 0)
            
                self.mc = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER,
                                         #szBackend=wx.media.MEDIABACKEND_DIRECTSHOW
                                         #szBackend=wx.media.MEDIABACKEND_QUICKTIME
                                         #szBackend=wx.media.MEDIABACKEND_WMP10
                                         )
                self.mc.Hide()
                
                self.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)

                btn1 = wx.Button(self, -1, u"打开文件")
                self.Bind(wx.EVT_BUTTON, self.OnLoadFile, btn1)

                btn2 = wx.Button(self, -1, u"播放")
                btn2.Disable()
                self.Bind(wx.EVT_BUTTON, self.OnPlay, btn2)
                self.playBtn = btn2

                btn3 = wx.Button(self, -1, u"暂停")
                btn3.Disable()
                self.Bind(wx.EVT_BUTTON, self.OnPause, btn3)
                self.pauseBtn = btn3
                
                btn4 = wx.Button(self, -1, u"停止")
                btn4.Disable()
                self.Bind(wx.EVT_BUTTON, self.OnStop, btn4)
                self.stopBtn = btn4
                
                slider = wx.Slider(self, -1, 0, 0, 0)
                self.slider = slider
                slider.SetMinSize((300, -1))
                self.Bind(wx.EVT_SLIDER, self.OnSeek, slider)
                
                self.VolumeCtrl = wx.Slider(self, value= 8, minValue=0, maxValue=10,
                        size=(80,-1),style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
                self.mc.SetVolume(0.8)
                self.Bind(wx.EVT_SLIDER, self.OnVolumeChange, self.VolumeCtrl)

                self.sliceShow = SliceVirtualList(self)
                
                # setup the layout
                sizer = wx.BoxSizer(wx.VERTICAL)
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.Add(btn1, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
                box.Add(btn2, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
                box.Add(slider, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 2)
                box.Add(btn3, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
                box.Add(btn4, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
                box.Add(self.VolumeCtrl, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
                
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 0)
                #sizer.Add(self.mc, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                sizer.Add(self.sliceShow, 3, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 0)
                self.SetSizer(sizer)
                sizer.Fit(self)
                
                self.SetBackgroundColour(wx.Colour(220, 220, 220))

                self.Center()
                
                self.taskBarIcon = MyTaskBarIcon(self, icon)
                self.taskBarIcon.ShowIcon(False)
                
                self.Bind(wx.EVT_CLOSE, self.OnClose)
                self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) 
                
                self.timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.OnTimer)
                                
        def OnLoadFile(self, evt):
                dlg = wx.FileDialog(self, message="Choose a media file",
                                    defaultDir=os.getcwd(), defaultFile="*.mp3",
                                    style=wx.OPEN | wx.CHANGE_DIR )
                if dlg.ShowModal() == wx.ID_OK:
                        path = dlg.GetPath()
                        self.DoLoadFile(path)
                dlg.Destroy()


        def DoLoadFile(self, path):
                self.playBtn.Disable()
                #noLog = wx.LogNull()
                if not self.mc.Load(path):
                        wx.MessageBox("Unable to load %s: Unsupported format?" % path,
                                  "ERROR",
                                  wx.ICON_ERROR | wx.OK)
                        self.playBtn.Disable()
                        self.pauseBtn.Disable()
                        self.stopBtn.Disable()  
                else:
                        self.playBtn.Enable()
                        self.pauseBtn.Enable()
                        self.stopBtn.Enable()
                        self.LoadLrcFile(path)
                        self.mc.SetInitialSize()
                        self.GetSizer().Layout()
                        self.slider.SetRange(0, self.mc.Length())

        def LoadLrcFile(self, path) :
                (filename, any) = os.path.splitext(path)
                lrcFile = filename + '.lrc'
                try:
                        f = open(lrcFile, 'rb')
                        lrcString = f.read()
                        f.close()
                        lrc = lrcParser.lrc(lrcString)
                        tagText = lrc.format()
                        self.textShow.SetTagValue(tagText)
                except IOError, e:
                        self.textShow.SetTagValue(None)
                        pass
                        
        def OnMediaLoaded(self, evt):
                self.playBtn.Enable()

        def OnPlay(self, evt):
                if not self.mc.Play():
                    wx.MessageBox("Unable to Play media : Unsupported format?",
                                  "ERROR",
                                  wx.ICON_ERROR | wx.OK)
                else:
                    self.mc.SetInitialSize()
                    self.GetSizer().Layout()
                    self.slider.SetRange(0, self.mc.Length())
                    self.timer.Start(50)

        def OnPause(self, evt):
                self.mc.Pause()

        def OnStop(self, evt):
                self.mc.Stop()

        def OnSeek(self, evt):
                offset = self.slider.GetValue()
                self.mc.Seek(offset)
        
        def OnSeletedText(self, evt):
                index = self.textShow.GetSelection()
                if self.textShow.tagValue == None or index == -1:
                        return 
                    
                offset = self.textShow.tagValue[0][index]
                self.textShow.MarkCurrentShow(offset) 
                self.mc.Seek(offset)
                
        def OnVolumeChange(self, evt) :
                self.mc.SetVolume(self.VolumeCtrl.GetValue() * 0.1)
                
        def OnTimer(self, evt):
                offset = self.mc.Tell()
                self.slider.SetValue(offset)
                statusText = str(offset/1000/60) + ':' + str(offset/1000%60) # + ':' + str((offset>>2) % 10)
                self.statusBar.SetStatusText(statusText)
                self.textShow.MarkCurrentShow(offset) 
        
        def OnIconfiy(self, event):
                self.Hide()
                self.taskBarIcon.ShowIcon(True)
                
        def OnClose(self, event):
                #print "begin closeing"              
                self.taskBarIcon.Destroy()
                self.timer.Stop()
                self.Destroy()        
                #print "end closeing"
		
# ############################################################  	                
class App(wx.App):
        def OnInit(self):
                wx.InitAllImageHandlers()
 
                self._mainFrame = MainFrame()
                self.SetTopWindow(self._mainFrame)
                self._mainFrame.Show(True)
        
                return True
                

if __name__ == "__main__":
	app = App(0)
        app.MainLoop()
