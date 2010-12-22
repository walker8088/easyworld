#coding:utf-8
#   Programmer: Daniel Pozmanter
#   E-mail:     drpython@bluebottle.com
#   Note:       You must reply to the verification e-mail to get through.
#
#   Copyright 2003-2007 Daniel Pozmanter
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#    DrPython is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#   Icons taken from "Noia Kde 100" by Carles Carbonell Bernado from the KDE-LOOK site (some edited a bit).
#   An excellent artist.

#Source Browser

import wx
import wx.stc
import re

import drScrolledMessageDialog
from drProperty import *

import config, glob
import EventManager

recolour = re.compile('#\w+')

def GetCount(line, compchar):
    l = len(line)
    x = 0
    y = 0
    while x < l:
        if line[x] == compchar:
            y = y + 1
        elif not line[x].isspace():
            x = l
        x = x + 1
    return y

class drTree(wx.TreeCtrl):
    def __init__(self, parent, id, point, size, style, ancestor):
        wx.TreeCtrl.__init__(self, parent, id, point, size, style)

        self.grandparent = ancestor
        self.parent = parent

        style = config.prefs.sourcebrowserstyle
        yarrr = convertStyleStringToWXFontArray(style)
        
        if config.prefs.sourcebrowseruseimages==1:
            imagesize = (16,16)

            self.imagelist = wx.ImageList(imagesize[0], imagesize[1])
            self.images = [
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/class.png", wx.BITMAP_TYPE_PNG)),
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/def.png", wx.BITMAP_TYPE_PNG)),
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/import.png", wx.BITMAP_TYPE_PNG)),
                wx.BitmapFromImage(wx.Image(config.BitmapDir + "/16/transparent.png", wx.BITMAP_TYPE_PNG))
                ]

            map(self.imagelist.Add, self.images)

            self.AssignImageList(self.imagelist)

        w = wx.Font(yarrr[1], wx.NORMAL, wx.NORMAL, wx.NORMAL, yarrr[2])

        w.SetFaceName(yarrr[0])

        if yarrr[3]:
            w.SetWeight(wx.BOLD)
        else:
            w.SetWeight(wx.NORMAL)
        if yarrr[4]:
            w.SetStyle(wx.ITALIC)
        else:
            w.SetStyle(wx.NORMAL)

        self.SetFont(w)

        f = convertColorPropertyToColorArray(getStyleProperty("fore", style))
        b = convertColorPropertyToColorArray(getStyleProperty("back", style))

        self.TextColor = wx.Colour(f[0], f[1], f[2])

        self.SetForegroundColour(self.TextColor)

        self.SetBackgroundColour(wx.Colour(b[0], b[1], b[2]))

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED,  self.OnItemActivated, id=id)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,  self.OnItemActivated, id=id)
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpandedCollapse, id=id)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnExpandedCollapse, id=id)

    def OnExpandedCollapse(self,event):
        event.Skip()
        #AB: it is necesserary to do something to refresh scroll bars
        
    def OnCompareItems(self, item1, item2):
        #Overriding Base, Return -1 for <, 0 for ==, +1 for >
        t1 = self.GetItemText(item1).lower()
        t2 = self.GetItemText(item2).lower()

        x = 0
        l = len(t1)
        if l > len(t2):
            l = len(t2)
        while x < l:
            if t1[x] < t2[x]:
                return -1
            elif t1[x] > t2[x]:
                return 1
            x = x + 1

        if l == len(t2):
            return -1

        return 0

    def OnItemActivated(self, event):
        sel = self.GetSelection()
        if not sel.IsOk():
            return
        t = self.GetItemText(sel)
        try:
            i = self.parent.ItemsIndex.index(sel)
            pos = self.parent.ItemsPos[i]
            
            line = glob.docMgr.currDoc.LineFromPosition(pos)
            
            if config.prefs.docfolding:
                glob.docMgr.currDoc.EnsureVisible(line)

            glob.docMgr.currDoc.ScrollToLine(line)
            glob.docMgr.currDoc.GotoLine(line)
            glob.docMgr.currDoc.GotoPos(pos)
            
            #self.grandparent.Raise()
            #self.grandparent.SetFocus()
            
            if config.prefs.sourcebrowsercloseonactivate:
                self.parent.OnBtnClose(event)
            else:
                glob.docMgr.currDoc.SetFocus()
        except:
            drScrolledMessageDialog.ShowMessage(self.parent, 'Error Activating Item', 'Source Browser Error')

class drSourceBrowserPanel(wx.Panel):
    def __init__(self, parent, id, Position, Index):
        wx.Panel.__init__(self, parent, id)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.mixed = 0

        self.renext = re.compile(r'^[ \t]*[^#^\s]', re.M)
        self.reinspect = re.compile(r'(^[ \t]*?class\s.*[(:])|(^[ \t]*?def\s.*[(:])|(^[ \t]*?import\s.*$)|(^[ \t]*?from\s.*$)|(^\s*#---.+)', 
                                re.MULTILINE)
        
        self.classtree = drTree(self, -1, wx.Point(0, 0), (400, 200), wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT, parent)

        #self.btnClose = wx.Button(self, 101, u"关闭(&Close)")
        self.btnRefresh = wx.Button(self, 102, u"刷新(&Refresh)")

        self.theSizer.Add(self.classtree, 9, wx.EXPAND)
        self.theSizer.Add(self.btnRefresh, 0, wx.EXPAND)
        
        #self.bSizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.bSizer.Add(self.btnRefresh, 0,  wx.SHAPED | wx.ALIGN_LEFT)
        #self.bSizer.Add(self.btnClose, 0,  wx.SHAPED | wx.ALIGN_LEFT)
        #self.edSearch = wx.TextCtrl(self, -1, "",size=(-1,-1)) #edit for search in tree
        #self.bSizer.Add(self.edSearch, 1,   wx.ALIGN_RIGHT)
        #self.theSizer.Add(self.bSizer, 0, wx.EXPAND)

        self.position = Position
        self.Index = Index

        #self.Bind(wx.EVT_BUTTON, self.OnBtnClose, id=101)
        self.Bind(wx.EVT_BUTTON, self.OnRefresh, id=102)
        
        glob.EventMgr.Bind(EventManager.EVT_SELECT_CHANGED, self.OnRefresh, None)
        glob.EventMgr.Bind(EventManager.EVT_FILE_CLOSED, self.OnFileClosed, None)
        
        #self.edSearch.Bind(wx.EVT_KEY_UP, self.OnEdSearch)
        #self.edSearch.SetToolTipString("Search in the class-tree")
        
        '''
        if not self.Browse():
            self.mixed = 1
            msg = 'This document is mixed.  It uses tabs and spaces for indentation.\nDrPython may not be able to correctly display the class browser.  Please use "Edit:Whitespace:Clean Up Indentation" to fix this.'
            drScrolledMessageDialog.ShowMessage(self, msg, "Check Indentation Results")
        '''
        
        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.Bind(wx.EVT_WINDOW_DESTROY,self.OnClose)

    def OnClose(self, event):
        pass
        
    def Browse(self):
        self.Index = glob.docMgr.selection
        
        if self.Index < 0 :
            self.classtree.DeleteAllItems()
            return 
            
        #Submitted Patch:  Christian Daven
        self.classtree.Freeze()
        #/Submitted Patch:  Christian Daven

        self.classtree.DeleteAllItems()

        self.root = self.classtree.AddRoot("")

        self.ItemsIndex = []

        self.ItemsPos = []

        self.eol = glob.docMgr.currDoc.GetEndOfLineCharacter()
        self.targetText = glob.docMgr.currDoc.GetText()
        
        #if self.mixed:
        #    return 
        
        RootArray = [self.root]
        Roots = [self.root]
        currentRoot = 0
        Indents = [0]
        currentIndent = 0

        #What is this document using?
        result = glob.docMgr.currDoc.CheckIndentation()
        wasnotmixed = 1
        if result == 0:
            wasnotmixed = 0
            if config.prefs.docusetabs[glob.docMgr.currDoc.filetype]:
                result = 1
            else:
                result = -1
        if result == 1:
            compchar = '\t'
            dec = 1
        else:
            compchar = ' '
            dec = config.prefs.doctabwidth[0]

        #Handle Triple Quoted Strings:
        self.targetText = self.RemoveTripleQuotedString(self.targetText)

        matcher = self.reinspect.finditer(self.targetText)

        #Get On With It!
        try:
            match = matcher.next()
        except:
            match = None
        while match is not None:
            matchedtext = match.group().strip()
            if matchedtext[0] == '#':
                nextmatch = self.renext.search(self.targetText[match.end():])

                indent = 0

                if nextmatch is not None:
                    indent = GetCount(nextmatch.group(), compchar)

                cR = currentRoot
                cI = currentIndent

                while indent < Indents[cI]:
                        cR = cR - 1
                        cI = cI - 1

                i = matchedtext[4:].find('---')
                if i > -1:
                    a = matchedtext[4:i+4]
                else:
                    a = matchedtext[4:]

                m = match.group().find('#')

                currentitem = self.classtree.AppendItem(Roots[cI], a)
                #applied patch from bug report [ 1215144 ], 11.04.2007:
                Roots.append(currentitem)
                self.classtree.SetPyData(Roots[-1], None)
                currentRoot += 1
                RootArray.append(Roots[currentRoot])
                self.ItemsIndex.append(currentitem)
                self.ItemsPos.append(match.start() + m)

                colours = recolour.findall(matchedtext)

                if len(colours) > 1:
                    try:
                        self.classtree.SetItemTextColour(currentitem, convertColorPropertyToColorArray(colours[0]))
                        self.classtree.SetItemBackgroundColour(currentitem, convertColorPropertyToColorArray(colours[1]))
                    except Exception, e:
                        print 'Error Setting Label Colour:', e
                self.classtree.SetItemImage(currentitem, 3, wx.TreeItemIcon_Normal)
                self.classtree.SetItemImage(currentitem, 3, wx.TreeItemIcon_Expanded)
            else:
                indent = GetCount(match.group(), compchar)

                while indent < Indents[currentIndent]:
                        Roots.pop()
                        currentRoot = currentRoot - 1
                        Indents.pop()
                        currentIndent = currentIndent - 1

                Indents.append(indent + dec)
                currentIndent = currentIndent + 1
                currentitem = self.classtree.AppendItem(Roots[currentRoot], matchedtext)
                Roots.append(currentitem)
                #Submitted bugfix, Franz Steinhausler
                self.classtree.SetPyData(Roots[-1], None)
                currentRoot += 1
                RootArray.append(Roots[currentRoot])
                self.ItemsIndex.append(Roots[currentRoot])
                self.ItemsPos.append(match.start())
                if matchedtext[0] == 'c':
                    try:
                        fg, bg = convertStyleToColorArray(config.prefs.PythonStyleDictionary[5])
                        self.classtree.SetItemTextColour(Roots[currentRoot], fg)
                        self.classtree.SetItemBackgroundColour(Roots[currentRoot], bg)
                    except Exception, e:
                        print 'Error Setting Class Colour:', e
                    self.classtree.SetItemImage(Roots[currentRoot], 0, wx.TreeItemIcon_Normal)
                    self.classtree.SetItemImage(Roots[currentRoot], 0, wx.TreeItemIcon_Expanded)
                elif matchedtext[0] == 'd':
                    try:
                        fg, bg = convertStyleToColorArray(config.prefs.PythonStyleDictionary[8])
                        self.classtree.SetItemTextColour(Roots[currentRoot], fg)
                        self.classtree.SetItemBackgroundColour(Roots[currentRoot], bg)
                    except Exception, e:
                        print 'Error Setting Def Colour:', e
                    self.classtree.SetItemImage(Roots[currentRoot], 1, wx.TreeItemIcon_Normal)
                    self.classtree.SetItemImage(Roots[currentRoot], 1, wx.TreeItemIcon_Expanded)
                else:
                    self.classtree.SetItemImage(Roots[currentRoot], 2, wx.TreeItemIcon_Normal)
                    self.classtree.SetItemImage(Roots[currentRoot], 2, wx.TreeItemIcon_Expanded)
            try:
                match = matcher.next()
            except:
                match = None
        
        self.classtree.Thaw()
        
        return wasnotmixed
    
    '''
    def OnEdSearch(self, event): #search on tree
        o=event.GetEventObject()
        s=o.GetValue().lower()
        if len(s)<2: return
        
        #s=self.classtree.GetItemText(self.classtree.GetSelection())
        sel=self.classtree.GetSelection()
        found=False
        start=False
        
        #First try after selected item:
        for item in self.ItemsIndex:
            if start==True:
                z=self.classtree.GetItemText(item).lower()
                if z.find(s)>0:
                    self.classtree.SelectItem(item,True)
                    self.classtree.OnItemActivated(None)
                    o.SetFocus()
                    o.SetInsertionPointEnd()
                    found=True
                    break
            if item==sel:
                start=True
        
        #Second try from start
        if found==False:
            for item in self.ItemsIndex:
                z=self.classtree.GetItemText(item).lower()
                if z.find(s)>0:
                    self.classtree.SelectItem(item,True)
                    self.classtree.OnItemActivated(None)
                    o.SetFocus()
                    o.SetInsertionPointEnd()
                    break
        
        event.Skip()

    def OnBtnClose(self, event):
        #self.parent.PUnbind(self.parent.EVT_DRPY_DOCUMENT_CHANGED, self.OnRefresh)
        #self.parent.SourceBrowser = None
        #self.panelparent.ClosePanel(self.position, self.Index)
        pass
    '''
    
    def OnRefresh(self, event):
        self.Browse()
        if event is not None:
            event.Skip()
    
    def OnFileClosed(self, event):
        self.classtree.DeleteAllItems()
        if event is not None:
            event.Skip()
    
    def RemoveTripleQuotedString(self, text):
        text = self.RemoveStringTripleQuotedWith(text, "'''")
        text = self.RemoveStringTripleQuotedWith(text, '"""')
        return text

    def RemoveStringTripleQuotedWith(self, text, target):
        start = text.find(target)
        while start > -1:
            end = text[start+3:].find(target)
            if end == -1:
                text = text[:start]
            else:
                end = start + 3 + end
                text = text[:start] + "".zfill((end - start) + 3) + text[end+3:]
            start = text.find(target)
        return text
