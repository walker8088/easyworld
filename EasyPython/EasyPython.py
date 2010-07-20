#coding:utf-8

import sys, os, re, string
import time

import wx
from wax import *
 
import wx.lib.agw.aui as aui
from wx.lib.agw.aui import aui_switcherdialog as ASD
 
import config, glob, utils

from actions import *        
from Notebook import *
from DocManager import *
from PluginManager import *
from ShortcutManager import *

from drMenu import * 
from drPrompt import *
from drPrinter import *

from drSourceBrowser import drSourceBrowserPanel

#*******************************************************************************************************
class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, '', wx.DefaultPosition, (800, 600), name = "EasyPython")
          
        glob.MainFrame = self
        
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        config.Init()
        
        self.InitializeConstants()
        
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.BitmapFromImage(wx.Image(config.BitmapDir + "/EasyPython.png", wx.BITMAP_TYPE_PNG)))
        self.SetIcon(icon)
        
        glob.LoadRecentFiles()
        
        glob.pluginMgr = PluginManager(self) 
        glob.shortcutMgr = ShortcutManager()
  
        #self.RestoreWinInfo()
        
        glob.action = self.CreateActions()
        
        self.CreateMenus()

        self.CreateStatusBar()
        self.GetStatusBar().SetFieldsCount(3)
        self.GetStatusBar().SetStatusWidths([-0, -6, -4])

        self.CreateToolBars()
            
        self.docbook = DocNotebook(self)
        self.docMgr = glob.docMgr = DocManager(self, self.docbook)
        
        self._mgr.AddPane(self.docbook, aui.AuiPaneInfo().Name("docbook").
                          CenterPane().PaneBorder(False))
        
        self.SourceBrowser = drSourceBrowserPanel(self, -1, config.prefs.sourcebrowserpanel, -1)
    
        self._mgr.AddPane(self.SourceBrowser, aui.AuiPaneInfo().Name("source_browser").Caption(u"源代码浏览器").
                          Left().CloseButton(True).MaximizeButton(False).MinimizeButton(False).MinSize((250, -1)))
  
        self.infobook = aui.AuiNotebook(self, -1, (0, 0), wx.Size(430, 200), style = 0)
        self._mgr.AddPane(self.infobook, aui.AuiPaneInfo().Name("infobook").Bottom().CaptionVisible(False).PaneBorder(False))
        
        self.runPrompt = DrPrompt(self)
        self.infobook.AddPage(self.runPrompt, u"程序输出")
        
        glob.LoadPopUpFile()
        self.Printer = DrPrinter(self)
        
        self.Bind(wx.EVT_END_PROCESS,  self.OnProcessEnded, id=-1)
        
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_CLOSE, self.OnCloseW)
        
        self.CenterOnScreen()
        
        self._mgr.Update()
        
        self.docMgr.UpdateTitle()
        
        wx.CallAfter(self.Maximize)
    
    def CreateToolBars(self) :
        tb1 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb1.SetToolBitmapSize(wx.Size(32, 32))
        glob.action['new'].AppendToAuiToolBar(tb1)
        glob.action['open'].AppendToAuiToolBar(tb1)
        glob.action['save'].AppendToAuiToolBar(tb1)
        glob.action['save_all'].AppendToAuiToolBar(tb1)
        glob.action['print'].AppendToAuiToolBar(tb1)
        #tb1.SetCustomOverflowItems(prepend_items, append_items)
        tb1.Realize()
        self._mgr.AddPane(tb1, aui.AuiPaneInfo().Name("toolbar1").ToolbarPane().Top().PaneBorder(True))
            
        tb2 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb2.SetToolBitmapSize(wx.Size(32, 32))
        glob.action['cut'].AppendToAuiToolBar(tb2)
        glob.action['copy'].AppendToAuiToolBar(tb2)
        glob.action['paste'].AppendToAuiToolBar(tb2)
        tb2.AddSeparator()
        glob.action['undo'].AppendToAuiToolBar(tb2)
        glob.action['redo'].AppendToAuiToolBar(tb2)
        #glob.action['delete'].AppendToAuiToolBar(tb2)
        #tb1.SetCustomOverflowItems(prepend_items, append_items)
        tb2.Realize()
        self._mgr.AddPane(tb2, aui.AuiPaneInfo().Name("toolbar2").ToolbarPane().Top().PaneBorder(True))
        
        tb3 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb3.SetToolBitmapSize(wx.Size(32, 32))
        glob.action['check_syntax'].AppendToAuiToolBar(tb3)
        glob.action['run'].AppendToAuiToolBar(tb3)
        glob.action['end'].AppendToAuiToolBar(tb3)
        tb3.Realize()
        self._mgr.AddPane(tb3, aui.AuiPaneInfo().Name("toolbar3").ToolbarPane().Top().PaneBorder(True))
        
    def CreateActions(self) :
        acts = Actions(self)
        
        acts.AddAction("new",      u'新建文件', self.OnNewFile)
        acts.AddAction("open",     u'打开文件', self.OnOpenFile)
        acts.AddAction("save",     u'保存文件', self.OnSaveFile)
        acts.AddAction("save_all", u'全部保存', self.OnSaveAll)
        acts.AddAction("close",    u'关闭文件', self.OnCloseFile)
        acts.AddAction("close_all",             u'关闭文件', self.OnCloseAll)
        acts.AddAction("close_all_others",      u'关闭文件', self.OnCloseAllOthers)
        
        acts.AddAction("print",    u'打印',    self.OnPrintFile)
        
        acts.AddAction("cut",   u'剪切', self.OnCut)
        acts.AddAction("copy",  u'复制', self.OnCopy)
        acts.AddAction("paste", u'粘贴', self.OnPaste)
        #acts.AddAction("delete", u'删除', self.OnDelete)
        acts.AddAction("undo",  u'撤销', self.OnUndo)
        acts.AddAction("redo",  u'重做', self.OnRedo)
        
        acts.AddAction("check_syntax",  u'语法检查', self.OnCheckSyntax)
        acts.AddAction("run",           u'运行程序', self.OnRun)
        acts.AddAction("end",           u'结束运行', self.OnEnd)
                        
        #acts.AddAction('exit', u"退出系统", glob.getBitmap('exit'), self.OnCmdExit)
        
        #acts.AddAction('setup', u"系统设置", glob.getBitmap('options'), self.OnCmdSetup)
        
        return acts
        
    #Initialize menus for Advanced mode (more items)
    def CreateMenus(self):
        self.filemenu = drMenu(self)
        self.filemenu.Append(self.ID_NEW, u'新建(New)', False, 0)
        self.Bind(wx.EVT_MENU,  self.OnNewFile, id=self.ID_NEW)
        self.filemenu.Append(self.ID_OPEN, u'打开(Open)', True, 0)
        self.Bind(wx.EVT_MENU,  self.OnOpenFile, id=self.ID_OPEN)
        
        self.RecentMenu = wx.Menu()
        self.CreateRecentFileMenu()
        self.filemenu.AppendMenu(self.ID_OPEN_RECENT, u"打开最近的文件(Op&en Recent)", self.RecentMenu)
        
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_CLOSE, u'关闭(Close)', False, 0)
        self.Bind(wx.EVT_MENU,  self.OnCloseFile, id=self.ID_CLOSE)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_SAVE, u'保存(Save)', False, 0)
        self.Bind(wx.EVT_MENU,  self.OnSaveFile, id=self.ID_SAVE)
        self.filemenu.Append(self.ID_SAVE_AS, u'另存为(Save As)', True, 5)
        self.Bind(wx.EVT_MENU,  self.OnSaveAs, id=self.ID_SAVE_AS)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_PRINT, u'打印文件(Print File)', True, 0)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_EXIT, u'结束退出(Exit)', False, 1)
        
        #self.Bind(wx.EVT_MENU,  self.OnCloseAll, id=self.ID_CLOSE_ALL)
        #self.Bind(wx.EVT_MENU,  self.OnCloseAllOthers, id=self.ID_CLOSE_ALL_OTHER_DOCUMENTS)

        self.Bind(wx.EVT_MENU,  self.OnSaveAll, id=self.ID_SAVE_ALL)
        self.Bind(wx.EVT_MENU,  self.OnPrintFile, id=self.ID_PRINT)
        
        self.Bind(wx.EVT_MENU,  self.OnExit, id=self.ID_EXIT)

        self.commentmenu = drMenu(self)
        self.commentmenu.Append(self.ID_COMMENT_REGION, u'注释(Comment)')
        self.commentmenu.Append(self.ID_UNCOMMENT_REGION, u'注释清除(UnComment)')

        self.whitespacemenu = drMenu(self)
        self.whitespacemenu.Append(self.ID_INDENT_REGION, u'Indent', False, 0)
        self.whitespacemenu.Append(self.ID_DEDENT_REGION, u'Dedent', False, 0)
        
        self.whitespacemenu.AppendSeparator()
        
        self.whitespacemenu.Append(self.ID_CHECK_INDENTATION, u"Check Indentation Type...")
        self.whitespacemenu.Append(self.ID_CLEAN_UP_TABS, u"Set Indentation To Tabs...")
        self.whitespacemenu.Append(self.ID_CLEAN_UP_SPACES, u"Set Indentation To Spaces...")
        
        #self.whitespacemenu.AppendSeparator()
        #self.whitespacemenu.Append(self.ID_UNIXMODE, u"Set Line Endings To Unix Mode (\"\\n\')")
        #self.whitespacemenu.Append(self.ID_WINMODE, u"Set Line Endings To DOS/Windows Mode (\"\\r\\n\')")
        #self.whitespacemenu.Append(self.ID_MACMODE, u"Set Line Endings To Mac Mode (\"\\r\')")

        self.casemenu = drMenu(self)
        self.casemenu.Append(self.ID_UPPERCASE, u'大写(Uppercase)', False, 0)
        self.Bind(wx.EVT_MENU,  self.OnUppercase, id=self.ID_UPPERCASE)
        self.casemenu.Append(self.ID_LOWERCASE, u'小写(Lowercase)', False, 0)
        self.Bind(wx.EVT_MENU,  self.OnLowercase, id=self.ID_LOWERCASE)
        
        self.editmenu = drMenu(self)
              
        self.editmenu.Append(self.ID_UNDO, u'撤销(Undo)', False, 0)
        self.Bind(wx.EVT_MENU,  self.OnUndo, id=self.ID_UNDO)
        self.editmenu.Append(self.ID_REDO, u'重做(Redo)', False, 1)
        self.Bind(wx.EVT_MENU,  self.OnRedo, id=self.ID_REDO)
        self.editmenu.AppendSeparator()

        self.editmenu.Append(self.ID_CUT, u'剪切(Cut)')
        self.editmenu.Append(self.ID_COPY, u'复制(Copy)')
        self.editmenu.Append(self.ID_PASTE, u'粘帖(Paste)')
        self.editmenu.Append(self.ID_DELETE, u'删除(Delete)')

        self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_SELECT_ALL, u'全选(Select All)')
        self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_FIND_AND_COMPLETE, u'查找并完成(Find And Complete)')
        self.editmenu.AppendSeparator()
        self.editmenu.AppendMenu(self.ID_COMMENT, u"注释(&Comments)", self.commentmenu)
        #self.editmenu.AppendMenu(self.ID_WHITESPACE, u"空白(&Whitespace)", self.whitespacemenu)
        self.editmenu.AppendMenu(self.ID_CASE, u"大小写(Case)", self.casemenu)

        self.Bind(wx.EVT_MENU,  self.OnMenuFind, id=self.ID_FIND)
        self.Bind(wx.EVT_MENU,  self.OnMenuFindNext, id=self.ID_FIND_NEXT)
        self.Bind(wx.EVT_MENU,  self.OnMenuFindPrevious, id=self.ID_FIND_PREVIOUS)
        self.Bind(wx.EVT_MENU,  self.OnMenuReplace, id=self.ID_REPLACE)

        self.Bind(wx.EVT_MENU,  self.OnSelectAll, id=self.ID_SELECT_ALL)

        self.Bind(wx.EVT_MENU,  self.OnIndentRegion, id=self.ID_INDENT_REGION)
        self.Bind(wx.EVT_MENU,  self.OnDedentRegion, id=self.ID_DEDENT_REGION)

        self.Bind(wx.EVT_MENU,  self.OnCommentRegion, id=self.ID_COMMENT_REGION)
        self.Bind(wx.EVT_MENU,  self.OnUnCommentRegion, id=self.ID_UNCOMMENT_REGION)
        
        self.searchmenu = drMenu(self)
        self.searchmenu.Append(self.ID_FIND, u'查找(Find)', True, 0)
        self.searchmenu.Append(self.ID_FIND_NEXT, u'查找下一个(Find Next)', False, 5)
        self.searchmenu.Append(self.ID_FIND_PREVIOUS, u'查找前一个(Find Previous)')
        self.searchmenu.Append(self.ID_REPLACE, u'替换(Replace)', True, 0)

        self.HightLightMenu = drMenu(self)
        self.HightLightMenu.AppendRadioItem(self.ID_HIGHLIGHT_PYTHON, "Python")
        self.HightLightMenu.AppendRadioItem(self.ID_HIGHLIGHT_HTML, "HTML")
        self.HightLightMenu.AppendRadioItem(self.ID_HIGHLIGHT_PLAIN_TEXT, "Plain Text")
        self.HightLightMenu.Check(self.ID_HIGHLIGHT_PYTHON, True)
        
        self.viewmenu = drMenu(self)
        self.viewmenu.AppendMenu(self.ID_HIGHLIGHT, u"语法高亮(&Syntax Highlighting)", self.HightLightMenu)
        self.viewmenu.AppendSeparator()
        self.viewmenu.Append(self.ID_TOGGLE_SOURCEBROWSER, u'切换源代码浏览器(Toggle Source Browser)')
        #self.viewmenu.Append(self.ID_SOURCEBROWSER_GOTO, u'Source Browser Go To', True)
        self.viewmenu.AppendSeparator()
        #fix bug someone refered in forum limodou 2004/04/20
        self.viewmenu.Append(self.ID_TOGGLE_VIEWWHITESPACE, u'Toggle View Whitespace', False, 12)
        #end limodou
        self.viewmenu.Append(self.ID_TOGGLE_PROMPT, u'Toggle Prompt')
        
        self.Bind(wx.EVT_MENU,  self.OnSyntaxHighlightingPython, id=self.ID_HIGHLIGHT_PYTHON)
        self.Bind(wx.EVT_MENU,  self.OnSyntaxHighlightingHTML, id=self.ID_HIGHLIGHT_HTML)
        self.Bind(wx.EVT_MENU,  self.OnSyntaxHighlightingText, id=self.ID_HIGHLIGHT_PLAIN_TEXT)
       
        self.ProgramMenu = drMenu(self)
        self.ProgramMenu.Append(self.ID_CHECK_SYNTAX, u'语法检查(Check Syntax)')
        self.ProgramMenu.AppendSeparator()
        self.ProgramMenu.Append(self.ID_RUN, u'运行(Run)')
        self.ProgramMenu.Append(self.ID_END, u'结束(End)')
        #self.ProgramMenu.AppendSeparator()
        self.ProgramMenu.Append(self.ID_SET_ARGS, u'设定运行参数(Set Arguments)', True)
        self.ProgramMenu.AppendSeparator()
        self.ProgramMenu.Append(self.ID_PYTHON, u'运行Python解释器(Run Python Interpreter)')
        #self.ProgramMenu.Append(self.ID_CLOSE_PROMPT, u'关闭Python解释器(Close Prompt)')
        #self.Bind(wx.EVT_MENU,  self.OnClosePrompt, id=self.ID_CLOSE_PROMPT)

        self.Bind(wx.EVT_MENU,  self.OnRun, id=self.ID_RUN)
        self.Bind(wx.EVT_MENU,  self.OnSetArgs, id=self.ID_SET_ARGS)
        self.Bind(wx.EVT_MENU,  self.OnPython, id=self.ID_PYTHON)
        self.Bind(wx.EVT_MENU,  self.OnEnd, id=self.ID_END)
        self.Bind(wx.EVT_MENU,  self.OnCheckSyntax, id=self.ID_CHECK_SYNTAX)
        
        self.optionsmenu = drMenu(self)
        self.optionsmenu.Append(self.ID_PREFS, u'参数设定(Preferences)', True, 0)
        self.Bind(wx.EVT_MENU,  self.OnPrefs, id=self.ID_PREFS)
        
        self.helpmenu = drMenu(self)
        self.helpmenu.Append(self.ID_ABOUT, u"关于(&About) EasyPython...")
        self.Bind(wx.EVT_MENU,  self.OnViewAbout, id=self.ID_ABOUT)
        self.helpmenu.AppendSeparator()
        self.helpmenu.Append(self.ID_HELP, 'Help', True, 0, u'EasyPython 帮助(&Help)...')
        self.Bind(wx.EVT_MENU,  self.OnViewHelp, id=self.ID_HELP)

        self.menuBar = wx.MenuBar()
       
        menuBarNames = [u"文件(&File)", u"编辑(&Edit)", u"搜索(&Search)", u"视图(&View)", u"程序(&Program)", u"书签(&Bookmarks)",
                         u"脚本(D&rScript)", u"选项(&Options)", u"帮助(&Help)"]

        self.menuBar.Append(self.filemenu, menuBarNames[0])
        self.menuBar.Append(self.editmenu, menuBarNames[1])
        self.menuBar.Append(self.searchmenu, menuBarNames[2])
        self.menuBar.Append(self.viewmenu, menuBarNames[3])
        self.menuBar.Append(self.ProgramMenu, menuBarNames[4])
        self.menuBar.Append(self.optionsmenu, menuBarNames[7])
        self.menuBar.Append(self.helpmenu, menuBarNames[8])

        self.SetMenuBar(self.menuBar)
                             
        self.Bind(wx.EVT_MENU,  self.OnToggleSourceBrowser, id=self.ID_TOGGLE_SOURCEBROWSER)
        self.Bind(wx.EVT_MENU,  self.OnToggleViewWhiteSpace, id=self.ID_TOGGLE_VIEWWHITESPACE)
        self.Bind(wx.EVT_MENU,  self.OnTogglePrompt, id=self.ID_TOGGLE_PROMPT)

    def OnActivate(self):
        glob.docMgr.UpdateDocs()
    
    def OnKeyDown(self, event):
        self.RunShortcuts(event)
        event.Skip()

    def OnExit(self, event):
        self.Close(False)

    def OnCloseW(self, event):
        glob.IgnoreEvents = True
        if not event.CanVeto():   
               return 
               
        x = 0
        l = len(glob.docMgr.docs)
        while x < l:
            if glob.docMgr.docs[x].GetModify():
                answer = wx.MessageBox(u'你需要保存"%s"吗?' % glob.docMgr.docs[x].GetFileName(),
                    "EasyPython", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                if answer == wx.YES:
                    glob.docMgr.SelectDoc(x)
                    self.OnSaveFile(event)
                elif answer == wx.CANCEL:
                    return
            x = x + 1
    
        event.Skip()

    #**********************************************************************************
    def OnNewFile(self, event):
        glob.docMgr.NewDoc()
        
    def OnOpenFile(self, event):
        #dlg = drFileDialog.FileDialog(self, "Open", config.prefs.wildcard, MultipleSelection=True, ShowRecentFiles=True)
        dlg = wx.FileDialog(self, u"打开文件", wildcard = u"Python 文件(*.py;*.pyw)|*.py;*.pyw|所有文件 (*.*)|*.*")
        dlg.SetDirectory(glob.CurrDir)
            
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            filenames = map(lambda x: x.replace("\\", '/'), filenames)

            for fname in filenames:
                glob.docMgr.OpenOrSwitchToFile(fname)

        dlg.Destroy()

    def OnOpenRecentFile(self, event):
        recentmenuindex = event.GetId() - self.ID_RECENT_FILES_BASE
        glob.docMgr.OpenOrSwitchToFile(glob.RecentFiles[recentmenuindex])

    def OnSaveFile(self, event):
        if not glob.docMgr.currDoc.filename:
            return self.OnSaveAs(event)
        else:
            glob.docMgr.SaveFile(glob.docMgr.selection)
        return True

    def OnSaveAs(self, event):
        #dlg = drFileDialog.FileDialog(self, "Save File As", config.prefs.wildcard, IsASaveDialog=True)
        dlg = wx.FileDialog(self, u"文件另存为", wildcard = u"Python 文件(*.py;*.pyw)|*.py;*.pyw|所有文件 (*.×)|*.×", style = wx.FD_SAVE)
        
        dlg.SetDirectory(glob.CurrDir)
        
        if dlg.ShowModal() != wx.ID_OK:
            return False 
            
        old = glob.docMgr.currDoc.filename
        
        if glob.docMgr.currDoc.untitlednumber > 0:
            glob.docMgr.currDoc.untitlednumber = -1
        
        glob.docMgr.currDoc.filename = dlg.GetPath().replace("\\", "/")
        glob.CurrDir = os.path.dirname(glob.docMgr.currDoc.filename)
        
        if not glob.docMgr.SaveFile(glob.docMgr.selection, not (old == glob.docMgr.currDoc.filename)):
            glob.docMgr.currDoc.filename = old
            return False
        
        #self.UpdateMenuAndToolbar()
        self.docMgr.UpdateTitle()

        glob.docMgr.UpdateHighLightMenu()
        glob.docMgr.currDoc.SetupPrefsDocument()
        
        #Update Recent Files
        self.DestroyRecentFileMenu()
        if glob.RecentFiles.count(glob.docMgr.currDoc.filename) != 0:
            glob.RecentFiles.remove(glob.docMgr.currDoc.filename)
        if len(glob.RecentFiles) == config.prefs.recentfileslimit:
            glob.RecentFiles.pop()
        glob.RecentFiles.insert(0, glob.docMgr.currDoc.filename)
        glob.WriteRecentFiles()
        self.CreateRecentFileMenu()
        
        dlg.Destroy()
        
        return True
        
    def OnSaveAll(self, event):
        oldpos = glob.docMgr.selection

        x = 0
        if config.prefs.promptonsaveall:
            tosaveArray = []
            tosaveLabels = []
            for document in glob.docMgr.docs:
                if glob.docMgr.docs[x].GetModify():
                    tosaveArray.append(x)
                    tosaveLabels.append(glob.docMgr.docs[x].GetFileNameTitle())
                x += 1
            if not tosaveLabels:
                return
            d = wx.lib.dialogs.MultipleChoiceDialog(self, u"需要保存所有的文件吗?", u"全部保存(Save All)", tosaveLabels, size=(300, 300))
            l = len(tosaveArray)
            y = 0
            while y < l:
                d.lbox.SetSelection(y)
                y += 1
            answer = d.ShowModal()
            selections = d.GetValue()
            d.Destroy()
            if answer == wx.ID_OK:
                for selection in selections:
                    if not glob.docMgr.docs[tosaveArray[selection]].filename:
                        glob.docMgr.SelectDoc(tosaveArray[selection])
                        self.OnSaveAs(None)
                    else:
                        glob.docMgr.SaveFile(tosaveArray[selection])
            else:
                return False
        else:
            for document in glob.docMgr.docs:
                if glob.docMgr.docs[x].GetModify():
                    if not glob.docMgr.docs[x].filename:
                        glob.docMgr.SelectDoc(x)
                        self.OnSaveAs(None)
                    else:
                        glob.docMgr.SaveFile(x)
                x += 1

        glob.docMgr.SelectDoc(oldpos)

        return True

    def OnCloseFile(self, event):
        if glob.docMgr.selection >= 0 :
            glob.docMgr.CloseDoc(glob.docMgr.selection)
    
    def OnCloseAll(self, event):
        x = len(glob.docMgr.docs) - 1
        while x > -1:
            glob.docMgr.SelectDoc(x)
            if glob.docMgr.currDoc.GetModify():
                if utils.Ask(u'你需要保存"%s"吗?' % glob.docMgr.currDoc.GetFileName(), "EasyPython"):
                    self.OnSave(event)
            glob.docMgr.CloseDoc(i)
            x = x - 1

    def OnCloseAllOthers(self, event):
        if not glob.docMgr.currDoc.filename:
            return
        farray = map(lambda document: document.filename, glob.docMgr.docs)
        try:
            i = farray.index(glob.docMgr.currDoc.filename)
        except:
            return

        x = len(farray) - 1
        while x > -1:
            if x != i:
                glob.docMgr.SelectDoc(x)
                if glob.docMgr.currDoc.GetModify():
                    if utils.Ask(u'你需要保存文件"%s"吗?' % glob.docMgr.currDoc.GetFileName(), "EasyPython"):
                        self.OnSaveFile(event)
                self.OnClose(event)
            x = x - 1
        
    def OnPrintFile(self, event):
        if not glob.docMgr.currDoc :
                return
        self.Printer.Print(glob.docMgr.currDoc.GetText(), glob.docMgr.currDoc.filename, 1)
    
    #**********************************************************************************
    def OnCheckSyntax(self, event):
        if glob.docMgr.selection < 0 :
                return
        if glob.docMgr.CheckSyntax(glob.docMgr.selection):
            self.SetStatusText(u'语法检查通过', 2)

    def OnPython(self, event):
        import win32process
        self.handle = win32process.CreateProcess(config.pythexec,
                config.pythexec, None, None, 0,
                win32process.CREATE_NEW_CONSOLE, 
                None , 
                None,
                win32process.STARTUPINFO()
                )
            
    def OnRun(self, event):
        if glob.docMgr.selection < 0 :
                return
        #patch [ 1367222 ] Improved Run Command + HTML Browser
        if glob.docMgr.currDoc.GetModify():
            if not utils.Ask(u"文件已经被修改了,必须保存后才能运行.\n你需要保存文件吗?", "EasyPython"):
                return
            if not self.OnSaveFile(event):
                return
            
        if not utils.IsPythonFile(glob.docMgr.currDoc.filename):
                return
                
        cwd = os.getcwd()
        
        cdir, filen = os.path.split(glob.docMgr.currDoc.filename)
        try:
            os.chdir(cdir)
        except:
            utils.ShowMessage(u"不能转换当前目录到:%s." % cdir, u"EasyPython运行错误")
            return
            
        largs = ""
        if (len(glob.LastProgArgs) > 0):
                largs = ' ' + glob.LastProgArgs
                
        if config.PLATFORM_IS_WIN:
                self.RunCmd((config.pythexecw + " -u " +  config.prefs.pythonargs + ' "' +
                         glob.docMgr.currDoc.filename.replace("\\", "/") + '"' + largs),
                         "Running " + filen, filen)
        else:
                self.RunCmd((config.pythexec + " -u " +  config.prefs.pythonargs + ' "' + glob.docMgr.currDoc.filename + '"'  + largs), 
                        "Running " + filen, filen)                #patch: [ 1366679 ] Goto Line Should Not Display At Top Of Window
        os.chdir(cwd)

    def OnSetArgs(self, event):
        d = wx.TextEntryDialog(self, "Arguments:", "EasyPython - Set Arguments", glob.LastProgArgs)
        if d.ShowModal() == wx.ID_OK:
            glob.LastProgArgs = d.GetValue()
        d.Destroy()

    def OnEnd(self, event):
        return
        if self.txtPrompt.pid != -1:
            self.infobook.SetPageImage(self.promptPosition, 2)
            self.UpdateMenuAndToolbar()
            wx.Process_Kill(self.txtPrompt.pid, wx.SIGKILL)
            self.txtPrompt.SetReadOnly(1)

    def OnProcessEnded(self, event):
        #Set the process info to the correct position in the array.
    
        i = 0
        epid = event.GetPid()
        
        try:
            i = map(lambda tprompt: tprompt.pid == epid, self.prompts).index(True)
        except:
            return

        #First, check for any leftover output.
        self.prompts[i].OnIdle(event)

        #If this is the process for the current window:
        if self.promptPosition == i:
            self.txtPrompt.process.Destroy()
            self.txtPrompt.process = None
            self.txtPrompt.pid = -1
            self.txtPrompt.SetReadOnly(1)
            self.txtPrompt.pythonintepreter = 0
            self.UpdateMenuAndToolbar()
            self.SetStatusText("", 2)
            self.infobook.SetPageImage(i, 2)
        else:
            self.prompts[i].process.Destroy()
            self.prompts[i].process = None
            self.prompts[i].pid = -1
            self.prompts[i].SetReadOnly(1)
            self.prompts[i].pythonintepreter = 0
            self.infobook.SetPageImage(i, 0)
            
        glob.docMgr.currDoc.SetFocus()
    
    #**********************************************************************************
    def OnPrefs(self, event):
        from drPrefsDialog import drPrefsDialog
        d = drPrefsDialog(self, -1, "EasyPython - Preferences")
        d.ShowModal()
        d.Destroy()
        
    #**********************************************************************************
    def OnNewPrompt(self, event):
        l = len(self.prompts)

        nextpage = drPanel(self.infobook, self.ID_APP)
        self.prompts.append(DrPrompt(nextpage, self.ID_APP, self))
        nextpage.SetSTC(self.prompts[l])
        
        self.infobook.AddPage(nextpage, "Prompt")

        self.prompts[l].Finder.Copy(self.txtPrompt.Finder)

        self.setPromptTo(l)
        
        self.txtPrompt.SetupPrefsPrompt(1)
        self.txtPrompt.SetSTCFocus(True)
    
    def OnClosePrompt(self, event):
        oldpos = self.promptPosition
        oldfinder = self.prompts[oldpos].Finder
        self.OnEnd(None)

        if len(self.prompts) > 1:
            self.prompts.pop(self.promptPosition)

            self.infobook.DeletePage(self.promptPosition)
            if self.promptPosition > 0:
                self.promptPosition = self.promptPosition - 1
            elif len(self.prompts) > 1:
                if self.promptPosition > 0:
                    self.promptPosition = self.promptPosition + 1
            self.setPromptTo(self.promptPosition)
            if oldpos > self.promptPosition:
                if self.txtPrompt.Finder:
                    self.txtPrompt.Finder.Copy(oldfinder)
        else:
            self.txtPrompt.SetText("")
            self.txtPrompt.EmptyUndoBuffer()
            self.txtPrompt.SetSavePoint()
            self.UpdateMenuAndToolbar()
            self.infobook.SetPageText(self.promptPosition, "Prompt")
            #The set size stuff ensures that wx.widgets repaints the tab.
            x, y = self.GetSizeTuple()
            self.SetSize((x-1, y-1))
            self.SetSize((x, y))


        self.infobook.OnPageChanged(None)
        
    def OnTogglePrompt(self, event):
        if self.mainpanel.PromptIsVisible:
            self.mainpanel.PromptIsVisible = False
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  False)
            glob.docMgr.currDoc.SetFocus()
        else:
            self.mainpanel.PromptIsVisible = True
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  True)
            self.txtPrompt.SetFocus()

    #**********************************************************************************
    def OnToggleSourceBrowser(self, event):
        pass
    
    #**********************************************************************************
    def OnSourceBrowserGoTo(self, event):
        drSourceBrowserGoTo.SourceBrowserGoTo(self, glob.docMgr.currDoc)

    def OnSyntaxHighlightingPython(self, event):
        glob.docMgr.currDoc.filetype = glob.PYTHON_FILE
        glob.docMgr.currDoc.SetupPrefsDocument()

    def OnSyntaxHighlightingHTML(self, event):
        glob.docMgr.currDoc.filetype = glob.HTML_FILE
        glob.docMgr.currDoc.SetupPrefsDocument()

    def OnSyntaxHighlightingText(self, event):
        glob.docMgr.currDoc.filetype = glob.TEXT_FILE
        glob.docMgr.currDoc.SetupPrefsDocument()

    def OnToggleViewWhiteSpace(self, event):
        if self.txtPrompt.GetSTCFocus():
            c = self.txtPrompt.GetViewWhiteSpace()
            self.txtPrompt.SetViewWhiteSpace(not c)
            if config.prefs.vieweol:
                self.txtPrompt.SetViewEOL(not c)
        else:
            c = glob.docMgr.currDoc.GetViewWhiteSpace()
            glob.docMgr.currDoc.SetViewWhiteSpace(not c)
            if config.prefs.vieweol:
                glob.docMgr.currDoc.SetViewEOL(not c)

    #**********************************************************************************
    def OnFormatMacMode(self, event):
        glob.docMgr.FormatMode("Mac")
       
    def OnFormatUnixMode(self, event):
        glob.docMgr.FormatMode("Unix")
        
    def OnFormatWinMode(self, event):
        glob.docMgr.FormatMode("Win")
        
    def OnIndentRegion(self, event):
        self.docMgr.IndentRegion()
        
    def OnCleanUpSpaces(self, event):
        wx.BeginBusyCursor()
        glob.docMgr.currDoc.SetToSpaces(8)
        glob.docMgr.currDoc.OnModified(None)
        wx.EndBusyCursor()
    
    def OnCommentRegion(self, event):
        glob.docMgr.CommentRegion()
    
    def OnUnCommentRegion(self, event):
        glob.docMgr.UnCommentRegion()
            
    def OnDedentRegion(self, event):
        glob.docMgr.DedentRegion()
            
    #**********************************************************************************
    def OnMenuFind(self, event):
        stc = self.GetActiveSTC()
        d = drFindReplaceDialog(self, -1, "Find", stc)
        d.SetOptions(self.FindOptions)
        if stc.GetSelectionStart() < stc.GetSelectionEnd():
            d.SetFindString(stc.GetSelectedText())
        elif config.prefs.findreplaceundercursor:
            pos = stc.GetCurrentPos()
            d.SetFindString(stc.GetTextRange(stc.WordStartPosition(pos, 1), stc.WordEndPosition(pos, 1)))
        d.Show(True)

    def OnMenuFindNext(self, event):
        self.GetActiveSTC().Finder.DoFindNext()

    def OnMenuFindPrevious(self, event):
        self.GetActiveSTC().Finder.DoFindPrevious()

    def OnMenuReplace(self, event):
        stc = self.GetActiveSTC()
        d = drFindReplaceDialog(self, -1, "Replace", stc, 1)
        d.SetOptions(glob.ReplaceOptions)
        if stc.GetSelectionStart() < stc.GetSelectionEnd():
            d.SetFindString(stc.GetTextRange(stc.GetSelectionStart(), stc.GetSelectionEnd()))
        else:
            d.SetFindString(stc.Finder.GetFindText())
        d.Show(True)

    def OnSelectAll(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.SelectAll()
        else:
            glob.docMgr.currDoc.SelectAll()

    def OnCut(self, event):
        if self.txtPrompt.GetSTCFocus():
            stc = self.txtPrompt
        else:
            stc = glob.docMgr.currDoc

        stc.CmdKeyExecute(wx.stc.STC_CMD_CUT)
        
    def OnCopy(self, event):
        if self.txtPrompt.GetSTCFocus():
            stc = self.txtPrompt
        else:
            stc = glob.docMgr.currDoc

        stc.CmdKeyExecute(wx.stc.STC_CMD_COPY)
        
    def OnPaste(self, event):
        if self.txtPrompt.GetSTCFocus():
            stc = self.txtPrompt
        else:
            stc = glob.docMgr.currDoc

        stc.Paste()
        
    def OnDelete(self, event):
        if self.txtPrompt.GetSTCFocus():
            stc = self.txtPrompt
        else:
            stc = glob.docMgr.currDoc

        stc.CmdKeyExecute(wx.stc.STC_CMD_CLEAR)
    
    def OnUndo(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.Undo()
        else:
            glob.docMgr.currDoc.Undo()

    def OnRedo(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.Redo()
        else:
            glob.docMgr.currDoc.Redo()
            
    def OnUppercase(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.CmdKeyExecute(wx.stc.STC_CMD_UPPERCASE)
        else:
            glob.docMgr.currDoc.CmdKeyExecute(wx.stc.STC_CMD_UPPERCASE)
    
    def OnLowercase(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.CmdKeyExecute(wx.stc.STC_CMD_LOWERCASE)
        else:
            glob.docMgr.currDoc.CmdKeyExecute(wx.stc.STC_CMD_LOWERCASE)
        
    #**********************************************************************************
    def OnViewAbout(self, event):
        import drAboutDialog
        drAboutDialog.Show(self)

    def OnViewHelp(self, event):
        self.ViewURLInBrowser(config.AppDir + "/documentation/help.html")
        
    #**********************************************************************************
    def CreateRecentFileMenu(self):
        x = 0
        numfiles = len(glob.RecentFiles)
        while x < numfiles:
            self.RecentMenu.Append(self.ID_RECENT_FILES_BASE+x, glob.RecentFiles[x])
            self.Bind(wx.EVT_MENU,  self.OnOpenRecentFile, id=self.ID_RECENT_FILES_BASE+x)
            x = x + 1
    
    def DestroyRecentFileMenu(self):
        #You need to call this function BEFORE you update the list of recent files.
        x = 0
        mnuitems = self.RecentMenu.GetMenuItems()
        num = len(mnuitems)
        while x < num:
            self.RecentMenu.Remove(self.ID_RECENT_FILES_BASE+x)
            x = x + 1

    def UpdateSourceBrwser(self) :
        self.SourceBrowser.Browse()
          
    #**********************************************************************************
    def Execute(self, command, statustext = ''):
        if not statustext:
            statustext = "Running Command"
        self.RunCmd(command, statustext, command)
        
    def ExecuteWithPython(self, command = '', statustext = '', pythonargs='', pagetext='Python'):
        commandstring = string.join([' -u', pythonargs, config.prefs.pythonargs, command], ' ').rstrip()
        if config.PLATFORM_IS_WIN:
            self.RunCmd((config.pythexecw + commandstring), statustext, pagetext)
        else:
            self.RunCmd((config.pythexec + commandstring), statustext, pagetext)
    
    def RunCmd(self, command, statustext = "Running Command", pagetext="Prompt", redin="", redout = "", rederr=""):

        '''
        if self.txtPrompt.pid > -1:
            self.OnNewPrompt(None)
        '''
        #self.infobook.SetPageText(0, pagetext)

        self.runPrompt.SetReadOnly(0)
        self.runPrompt.SetText(command + '\n')
            
        #self.infobook.SetPageImage(self.promptPosition, 3)
        self.runPrompt.SetScrollWidth(1)
        self.runPrompt.editpoint = self.runPrompt.GetLength()
        self.runPrompt.GotoPos(self.runPrompt.editpoint)
        
        self.SetStatusText(statustext, 2)
        
        self.runPrompt.process = wx.Process(self)
        self.runPrompt.process.Redirect()
        
        if type(command) == unicode:
                command = command.encode(wx.GetDefaultPyEncoding())
                
        if config.PLATFORM_IS_WIN:
            self.runPrompt.pid = wx.Execute(command, wx.EXEC_ASYNC | wx.EXEC_NOHIDE, self.runPrompt.process)
        else:
            self.runPrompt.pid = wx.Execute(command, wx.EXEC_ASYNC, self.runPrompt.process)
        
        self.runPrompt.inputstream = self.runPrompt.process.GetInputStream()
        self.runPrompt.errorstream = self.runPrompt.process.GetErrorStream()
        self.runPrompt.outputstream = self.runPrompt.process.GetOutputStream()

        self.runPrompt.process.redirectOut = redout
        self.runPrompt.process.redirectErr = rederr
       
        self.runPrompt.SetFocus()

    #**********************************************************************************
    def GetActiveSTC(self):
        return glob.docMgr.currDoc

    #**********************************************************************************
    def InitializeConstants(self):
        
        self.ID_DOCUMENT_BASE = 50
        self.ID_PROMPT_BASE = 340

        #Application ID Constants
        self.ID_APP = 101

        self.ID_NEW = 102
        self.ID_OPEN = 103
        self.ID_OPEN_IMPORTED_MODULE = 1000
        self.ID_OPEN_RECENT = 104
        self.ID_RELOAD = 105
        self.ID_RESTORE_FROM_BACKUP = 1051

        self.ID_CLOSE = 106
        self.ID_CLOSE_ALL = 6061
        self.ID_CLOSE_ALL_OTHER_DOCUMENTS = 6062
        self.ID_CLEAR_RECENT = 107

        self.ID_SAVE = 108
        self.ID_SAVE_AS = 109
        self.ID_SAVE_COPY = 1092
        self.ID_SAVE_ALL = 1098

        self.ID_PRINT_SETUP = 1010
        self.ID_PRINT = 1011

        self.ID_EXIT = 1014
        
        self.ID_COPY = 850
        self.ID_PASTE = 851
        self.ID_CUT = 852
        self.ID_DELETE = 853

        self.ID_FIND = 111
        self.ID_FIND_NEXT = 112
        self.ID_FIND_PREVIOUS = 1122
        self.ID_REPLACE = 113
        
        self.ID_SOURCEBROWSER_GOTO = 1157
        self.ID_SELECT_ALL = 1161
        self.ID_INSERT_REGEX = 1163

        self.ID_INSERT_SEPARATOR = 1164

        self.ID_COMMENT = 1116
        self.ID_COMMENT_REGION = 116
        self.ID_UNCOMMENT_REGION = 117

        self.ID_WHITESPACE = 1118
        self.ID_INDENT_REGION = 118
        self.ID_DEDENT_REGION = 119
        self.ID_CHECK_INDENTATION = 1650

        self.ID_CLEAN_UP_TABS = 1670
        self.ID_CLEAN_UP_SPACES = 1671

        self.ID_FORMATMENU = 2000
        self.ID_UNIXMODE = 2001
        self.ID_WINMODE = 2002
        self.ID_MACMODE = 2003

        self.ID_FIND_AND_COMPLETE = 2071

        self.ID_CASE = 1191
        self.ID_UPPERCASE = 1192
        self.ID_LOWERCASE = 1193

        self.ID_UNDO = 1111
        self.ID_REDO = 1112

        self.ID_ZOOM_IN = 161
        self.ID_ZOOM_OUT = 162
        self.ID_FOLDING = 1610
        self.ID_TOGGLE_FOLD = 1613
        self.ID_FOLD_ALL = 1611
        self.ID_EXPAND_ALL = 1612
        self.ID_TOGGLE_SOURCEBROWSER = 163
        self.ID_TOGGLE_VIEWWHITESPACE = 164
        self.ID_TOGGLE_PROMPT = 165

        self.ID_HIGHLIGHT = 580

        self.ID_HIGHLIGHT_PYTHON = 585
        self.ID_HIGHLIGHT_HTML = 587
        self.ID_HIGHLIGHT_PLAIN_TEXT = 589

        self.ID_RUN = 121
        self.ID_SET_ARGS = 122
        self.ID_PYTHON = 123
        self.ID_END = 125
        self.ID_CLOSE_PROMPT = 1250
        self.ID_CHECK_SYNTAX = 126

        self.ID_PREFS = 131
        self.ID_SHORTCUTS = 133
        self.ID_POPUP = 134
        self.ID_CUSTOMIZE_TOOLBAR = 135
        
        self.ID_EDIT_BOOKMARKS = 301
        self.ID_EDIT_SCRIPT_MENU = 3004

        self.ID_ABOUT = 140
        self.ID_HELP = 141

        self.ID_OTHER = 9000
        self.ID_RECENT_FILES_BASE = 9930
        self.ID_RECENT_SESSIONS_BASE = 8330
        self.ID_SCRIPT_BASE = 7500
        
    def RunShortcuts(self, event, stc = None, SplitView = 0):
        #return drShortcuts.RunShortcuts(glob.shortcutMgr, event, stc, SplitView)
        pass
        
    #**********************************************************************************
    def setPromptTo(self, number):
        oldfinder = self.prompts[self.promptPosition].Finder

        self.promptPosition = number
        self.txtPrompt = self.prompts[self.promptPosition]
        self.txtPrompt.Finder.Copy(oldfinder)
        self.currPrompt = self.infobook.GetPage(number)

        if self.prompts[self.promptPosition].pid != -1:
            if self.txtPrompt.pythonintepreter:
                self.SetStatusText("Running Python Interpreter", 2)
            else:
                self.SetStatusText(("Running " + os.path.split(glob.docMgr.currDoc.filename)[1]), 2)
        else:
            self.SetStatusText("", 2)

        self.infobook.SetSelection(self.promptPosition)
 
    def ShowPrompt(self, Visible = True):
        if Visible:
            if self.mainpanel.PromptIsVisible:
                return
            self.mainpanel.PromptIsVisible = True
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  True)
            self.txtPrompt.SetFocus()
        else:
            if not self.mainpanel.PromptIsVisible:
                return
            self.mainpanel.PromptIsVisible = False
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  False)
            glob.docMgr.currDoc.SetFocus()
        
    def updatePrefs(self, oldprefs):
        #Styling:
        
        for document in glob.docMgr.docs:
            document.StyleResetDefault()
            document.StyleClearAll()
            document.SetupPrefsDocument(0)

        #Find/Replace:
        if  (config.prefs.findreplaceregularexpression != oldprefs.findreplaceregularexpression) or \
        (config.prefs.findreplacematchcase != oldprefs.findreplacematchcase) or \
        (config.prefs.findreplacefindbackwards != oldprefs.findreplacefindbackwards) or \
        (config.prefs.findreplacewholeword != oldprefs.findreplacewholeword) or \
        (config.prefs.findreplaceinselection != oldprefs.findreplaceinselection) or \
        (config.prefs.findreplacefromcursor != oldprefs.findreplacefromcursor) or \
        (config.prefs.findreplacepromptonreplace != oldprefs.findreplacepromptonreplace):
            glob.FindOptions = []
            glob.ReplaceOptions = []

        if not (oldprefs.recentfileslimit == config.prefs.recentfileslimit):
            self.DestroyRecentFileMenu()
            glob.RecentFiles = []

            self.LoadRecentFiles()
            self.CreateRecentFileMenu()

        #Styling:
        glob.docMgr.currDoc.StyleResetDefault()
        glob.docMgr.currDoc.StyleClearAll()

        self.txtPrompt.StyleResetDefault()
        self.txtPrompt.StyleClearAll()

        glob.docMgr.currDoc.SetupPrefsDocument(0)
        if glob.docMgr.currDoc.GetViewWhiteSpace():
            glob.docMgr.currDoc.SetViewEOL(config.prefs.vieweol)
        self.txtPrompt.SetupPrefsPrompt(0)
        if self.txtPrompt.GetViewWhiteSpace():
            self.txtPrompt.SetViewEOL(config.prefs.vieweol)

        if oldprefs.docfolding[glob.docMgr.currDoc.filetype]:
            if not config.prefs.docfolding[glob.docMgr.currDoc.filetype]:
                glob.docMgr.currDoc.FoldAll(True)

        glob.docMgr.currDoc.OnModified(None)
        glob.docMgr.currDoc.OnPositionChanged(None)

        #Parenthesis Matching:
        if oldprefs.docparenthesismatching != config.prefs.docparenthesismatching:
            if not config.prefs.docparenthesismatching:
                #Clear Parenthesis Highlighting
                glob.docMgr.currDoc.BraceBadLight(wx.stc.STC_INVALID_POSITION)
                glob.docMgr.currDoc.BraceHighlight(wx.stc.STC_INVALID_POSITION, wx.stc.STC_INVALID_POSITION)

    def ViewURLInBrowser(self, url):
        if url.find('http:') == -1:
            url = os.path.normpath(url)
        if config.prefs.documentationbrowser == '<os.startfile>' and config.PLATFORM_IS_WIN:
            os.startfile(url)
            return
        wx.Execute((config.prefs.documentationbrowser + ' "' + url + '"'), wx.EXEC_ASYNC)

    #**********************************************************************************
    def GetNewId(self):
        return 10000 + wx.NewId()

    def GetPreference(self, pref, key=None):
        if key is not None:
            return config.prefs[pref][key]
        else:
            return config.prefs[pref]
    
    #**********************************************************************************
    # lm - adding helper functions
    def promptSaveAll(self):
        """ check if there are any open unsaved files, and prompt the user to save each """
        x = 0
        while x < len(glob.docMgr.docs):
            if glob.docMgr.docs[x].GetModify():
                if utils.Ask('Would you like to save "%s"?' % glob.docMgr.docs[x].GetFileName(), "EasyPython"):
                    glob.docMgr.SelectDoc(x)
                    self.OnSaveFile(None)
            x += 1

    def promptSaveCurrent(self):
        """ ask the user if they would like to save the current file """
        if glob.docMgr.currDoc.GetModify():
            if utils.Ask('Would you like to save "%s"?' % glob.docMgr.currDoc.GetFileName(), "EasyPython"):
                self.OnSaveFile(None)

    def promptDir(self, msg):
        """ open a directory browser and return the directory chosen """
        d = wx.DirDialog(self, msg, style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON|wx.MAXIMIZE_BOX|wx.THICK_FRAME)
        dir = ''
        if d.ShowModal() == wx.ID_OK:
            dir = d.GetPath()
        d.Destroy()
        return dir
        
    def RestoreWinInfo(self) :    
        WindowWidth = 800
        WindowHeight = 600
        wasMaximized = 0
        
        if not os.path.exists(config.AppDataDir + "/EasyPython.sizeandposition.dat"):
                return
        try:
            f = file(config.AppDataDir + "/EasyPython.sizeandposition.dat", 'r')
            text = f.read()
            if text:
                values = map(int, text.split('\n'))
                if len (values) == 5:
                    WindowWidth, WindowHeight, WindowX, WindowY, wasMaximized = values
                    self.SetSize((WindowWidth, WindowHeight))
                    self.Move(wx.Point(WindowX, WindowY))
                    if wasMaximized == 1:
                        wx.CallAfter(self.Maximize)
            f.close()
        except:
            pass
            
        
#*******************************************************************************************************
if __name__ == '__main__':
    app = Application(MainFrame)
    app.Run()