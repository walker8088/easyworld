#coding:utf-8

import sys, os, re, string
import time
import traceback
import subprocess

        
import wx
import wx.stc

if wx.Platform == '__WXMSW__':
   import win32api
   import win32gui     
   import win32con
 
import wx.lib.dialogs
import wx.lib.agw.aui as aui
from wx.lib.agw.aui import aui_switcherdialog as ASD
 
import config, EpyGlob, utils

from actions import *        
from Notebook import *
from EventManager import *
from DocManager import *
from PluginManager import *
from ShortcutManager import *

from drMenu import * 
from drPrompt import *
from drPrinter import *
from drFindReplaceDialog import *

from drSourceBrowser import drSourceBrowserPanel

#*******************************************************************************************************
class MainFrame(wx.Frame):
    ID_DOCUMENT_BASE = 50
    ID_PROMPT_BASE = 340
    
    ID_ABOUT = 140
    ID_HELP = 141

    ID_OTHER = 9000
    ID_RECENT_FILES_BASE = 9930
    ID_RECENT_SESSIONS_BASE = 8330
        
    def __init__(self):
        wx.Frame.__init__(self, None, -1, '', wx.DefaultPosition, (800, 600), name = "EasyPython")
        
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
          
        EpyGlob.mainFrame = self
        
        EpyGlob.EventMgr = EventManager.EventManager(self) 
        
        EpyGlob.EventMgr.Bind(EventManager.EVT_FILE_NEW, self.OnEventFileNew)
        
        #if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe":
        #    self.icon = win32gui.CreateIconFromResource(win32api.LoadResource(None, win32con.RT_ICON, 1), True)
        #else :
        self.icon = wx.Icon(os.path.join(config.AppDir, "EasyPython.ico"), wx.BITMAP_TYPE_ICO)
        
        self.SetIcon(self.icon)
        
        EpyGlob.LoadRecentFiles()
        
        EpyGlob.shortcutMgr = ShortcutManager()
  
        EpyGlob.action = self.CreateActions()
        
        self.CreateMenus()

        self.CreateStatusBar()
        self.GetStatusBar().SetFieldsCount(3)
        self.GetStatusBar().SetStatusWidths([-0, -6, -4])

        self.CreateToolBars()
            
        self.docbook = DocNotebook(self)
        self.docMgr = EpyGlob.docMgr = DocManager(self, self.docbook)
        
        self._mgr.AddPane(self.docbook, aui.AuiPaneInfo().Name("docbook").CenterPane().PaneBorder(False))
        
        self.SourceBrowser = drSourceBrowserPanel(self, -1, config.prefs.sourcebrowserpanel, -1)
    
        self._mgr.AddPane(self.SourceBrowser, aui.AuiPaneInfo().Name("source_browser").Caption(u"代码浏览器").
                          Right().Show(False).CloseButton(True).MaximizeButton(False).MinimizeButton(False).MinSize((250, -1)))
  
        self.infobook = aui.AuiNotebook(self, -1, (0, 0), wx.Size(430, 200), style = 0)
        self._mgr.AddPane(self.infobook, aui.AuiPaneInfo().Name("infobook").Bottom().Show(True).CaptionVisible(False).PaneBorder(False))
        
        self.txtPrompt = DrPrompt(self)
        self.infobook.AddPage(self.txtPrompt, u"程序输出")
        
        self.UpdateTitle()
        
        self.Printer = DrPrinter(self)
        
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_CLOSE, self.OnCloseW)
        
        #self.RestoreWinInfo()
        
        self.CenterOnScreen()
        self.Maximize()
        
        self._mgr.Update()
        
    def CreateToolBars(self) :
        tb1 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb1.SetToolBitmapSize(wx.Size(24,24))
        EpyGlob.action['open_history'].AppendToAuiToolBar(tb1)
        EpyGlob.action['open'].AppendToAuiToolBar(tb1)
        EpyGlob.action['new'].AppendToAuiToolBar(tb1)
        EpyGlob.action['save'].AppendToAuiToolBar(tb1)
        EpyGlob.action['save_all'].AppendToAuiToolBar(tb1)
        EpyGlob.action['save_as'].AppendToAuiToolBar(tb1)
        #EpyGlob.action['close'].AppendToAuiToolBar(tb1)
        tb1.AddSeparator()
        EpyGlob.action['print'].AppendToAuiToolBar(tb1)
        #tb1.SetCustomOverflowItems(prepend_items, append_items)
        tb1.Realize()
        self._mgr.AddPane(tb1, aui.AuiPaneInfo().Name("toolbar1").ToolbarPane().Top().PaneBorder(True))
            
        tb2 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb2.SetToolBitmapSize(wx.Size(24,24))
        EpyGlob.action['cut'].AppendToAuiToolBar(tb2)
        EpyGlob.action['copy'].AppendToAuiToolBar(tb2)
        EpyGlob.action['paste'].AppendToAuiToolBar(tb2)
        #EpyGlob.action['delete'].AppendToAuiToolBar(tb2)
        tb2.AddSeparator()
        EpyGlob.action['undo'].AppendToAuiToolBar(tb2)
        EpyGlob.action['redo'].AppendToAuiToolBar(tb2)
        tb2.AddSeparator()
        EpyGlob.action['comment'].AppendToAuiToolBar(tb2)
        EpyGlob.action['uncomment'].AppendToAuiToolBar(tb2)
        EpyGlob.action['indent'].AppendToAuiToolBar(tb2)
        EpyGlob.action['dedent'].AppendToAuiToolBar(tb2)
        tb2.Realize()
        self._mgr.AddPane(tb2, aui.AuiPaneInfo().Name("toolbar2").ToolbarPane().Top().PaneBorder(True))
        
        tb5 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb5.SetToolBitmapSize(wx.Size(24,24))
        EpyGlob.action['find'].AppendToAuiToolBar(tb5)
        EpyGlob.action['replace'].AppendToAuiToolBar(tb5)
        EpyGlob.action['find_next'].AppendToAuiToolBar(tb5)
        EpyGlob.action['find_prev'].AppendToAuiToolBar(tb5)
        tb5.Realize()
        self._mgr.AddPane(tb5, aui.AuiPaneInfo().Name("toolbar5").ToolbarPane().Top().PaneBorder(True))
         
        tb3 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb3.SetToolBitmapSize(wx.Size(24,24))
        EpyGlob.action['run_python'].AppendToAuiToolBar(tb3)
        EpyGlob.action['check_syntax'].AppendToAuiToolBar(tb3)
        EpyGlob.action['run'].AppendToAuiToolBar(tb3)
        EpyGlob.action['end'].AppendToAuiToolBar(tb3)
        tb3.Realize()
        self._mgr.AddPane(tb3, aui.AuiPaneInfo().Name("toolbar3").ToolbarPane().Top().PaneBorder(True))
        
        tb4 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb4.SetToolBitmapSize(wx.Size(24,24))
        EpyGlob.action['toggle_source_browser'].AppendToAuiToolBar(tb4)
        EpyGlob.action['preferences'].AppendToAuiToolBar(tb4)
        tb4.Realize()
        self._mgr.AddPane(tb4, aui.AuiPaneInfo().Name("toolbar4").ToolbarPane().Top().PaneBorder(True))
        
        tb_last = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb_last.SetToolBitmapSize(wx.Size(24,24))
        EpyGlob.action['about'].AppendToAuiToolBar(tb_last)
        EpyGlob.action['help'].AppendToAuiToolBar(tb_last)
        EpyGlob.action['exit'].AppendToAuiToolBar(tb_last)
        tb_last.Realize()
        self._mgr.AddPane(tb_last, aui.AuiPaneInfo().Name("toolbar_last").ToolbarPane().Top().PaneBorder(True))
        
    def CreateActions(self) :
        actions = Actions(self)
        
        actions.AddAction("new",      u'新建文件', self.OnNewFile)
        actions.AddAction("open",     u'打开文件', self.OnOpenFile)
        actions.AddAction("save",     u'保存文件', self.OnSaveFile)
        actions.AddAction("save_as",  u'另存为',   self.OnSaveAs)
        actions.AddAction("save_all", u'全部保存', self.OnSaveAll)
        
        actions.AddAction("close",    u'关闭文件', self.OnCloseFile, enabled = False)
        actions.AddAction("close_all",             u'关闭所有文件', self.OnCloseAll, enabled = False)
        actions.AddAction("close_all_others",      u'关闭所有其他文件', self.OnCloseAllOthers, enabled = False)
        
        actions.AddAction("open_history", u'最近打开的文件', self.OnOpenHistory)
        
        actions.AddAction("print",    u'打印',    self.OnPrintFile, enabled = False)
        
        actions.AddAction("cut",   u'剪切', self.OnCut)
        actions.AddAction("copy",  u'复制', self.OnCopy)
        actions.AddAction("paste", u'粘贴', self.OnPaste)
        actions.AddAction("delete", u'删除', self.OnDelete)
        actions.AddAction("undo",  u'撤销', self.OnUndo)
        actions.AddAction("redo",  u'重做', self.OnRedo)
        
        actions.AddAction("comment",  u'注释', self.OnCommentRegion)
        actions.AddAction("uncomment",  u'取消注释', self.OnUnCommentRegion)
        actions.AddAction("indent",  u'缩进', self.OnIndentRegion)
        actions.AddAction("dedent",  u'缩退', self.OnDedentRegion)
        
        actions.AddAction("find",  u'查找', self.OnFind)
        actions.AddAction("replace",  u'替换', self.OnReplace)
        actions.AddAction("find_next",  u'查找后一个', self.OnFindNext, enabled = False)
        actions.AddAction("find_prev",  u'查找前一个', self.OnFindPrevious, enabled = False)
        
        actions.AddAction("toggle_source_browser",  u'切换源代码浏览器', self.OnToggleSourceBrowser)
        actions.AddAction('preferences', u"系统设置", self.OnPrefs)
        
        actions.AddAction("check_syntax",  u'语法检查', self.OnCheckSyntax)
        actions.AddAction("run_python",    u'运行Python解释器', self.OnPython)
        actions.AddAction("run",           u'运行程序', self.OnRun)
        actions.AddAction("end",           u'结束运行', self.OnEnd, enabled = False)
                      
        actions.AddAction('about', "关于...", self.OnViewAbout)
        actions.AddAction('help', u"使用帮助", self.OnViewHelp)
        actions.AddAction('exit', u"退出系统", self.OnExit)
        
        return actions
        
    #Initialize menus for Advanced mode (more items)
    def CreateMenus(self):
        return
        self.whitespacemenu = drMenu(self)
        self.whitespacemenu.Append(self.ID_INDENT_REGION, u'Indent', False, 0)
        self.whitespacemenu.Append(self.ID_DEDENT_REGION, u'Dedent', False, 0)
        
        self.whitespacemenu.AppendSeparator()
        
        self.whitespacemenu.Append(self.ID_CHECK_INDENTATION, u"Check Indentation Type...")
        self.whitespacemenu.Append(self.ID_CLEAN_UP_TABS, u"Set Indentation To Tabs...")
        self.whitespacemenu.Append(self.ID_CLEAN_UP_SPACES, u"Set Indentation To Spaces...")
        
        self.Bind(wx.EVT_MENU,  self.OnIndentRegion, id=self.ID_INDENT_REGION)
        self.Bind(wx.EVT_MENU,  self.OnDedentRegion, id=self.ID_DEDENT_REGION)

        self.Bind(wx.EVT_MENU,  self.OnCommentRegion, id=self.ID_COMMENT_REGION)
        self.Bind(wx.EVT_MENU,  self.OnUnCommentRegion, id=self.ID_UNCOMMENT_REGION)
               
        self.ProgramMenu = drMenu(self)
        self.ProgramMenu.Append(self.ID_CHECK_SYNTAX, u'语法检查(Check Syntax)')
        self.ProgramMenu.AppendSeparator()
        self.ProgramMenu.Append(self.ID_RUN, u'运行(Run)')
        self.ProgramMenu.Append(self.ID_END, u'结束(End)')
        #self.ProgramMenu.AppendSeparator()
        self.ProgramMenu.Append(self.ID_SET_ARGS, u'设定运行参数(Set Arguments)', True)
        self.ProgramMenu.AppendSeparator()
        self.ProgramMenu.Append(self.ID_PYTHON, u'运行Python解释器(Run Python Interpreter)')
        
        self.Bind(wx.EVT_MENU,  self.OnRun, id=self.ID_RUN)
        self.Bind(wx.EVT_MENU,  self.OnSetArgs, id=self.ID_SET_ARGS)
        self.Bind(wx.EVT_MENU,  self.OnPython, id=self.ID_PYTHON)
        self.Bind(wx.EVT_MENU,  self.OnEnd, id=self.ID_END)
        self.Bind(wx.EVT_MENU,  self.OnCheckSyntax, id=self.ID_CHECK_SYNTAX)
        
        self.optionsmenu = drMenu(self)
        self.optionsmenu.Append(self.ID_PREFS, u'参数设定(Preferences)', True, 0)
        self.Bind(wx.EVT_MENU,  self.OnPrefs, id=self.ID_PREFS)
        
        self.menuBar = wx.MenuBar()
       
        menuBarNames = [u"文件(&File)", u"编辑(&Edit)", u"搜索(&Search)", u"视图(&View)", u"程序(&Program)", u"书签(&Bookmarks)",
                         u"脚本(D&rScript)", u"选项(&Options)", u"帮助(&Help)"]

        #self.menuBar.Append(self.ProgramMenu, menuBarNames[4])
        
        #self.SetMenuBar(self.menuBar)
                             
    def OnActivate(self):
        self.docMgr.UpdateDocs()
    
    def OnKeyDown(self, event):
        self.RunShortcuts(event)
        event.Skip()

    def OnExit(self, event):
        self.Close(False)

    def OnCloseW(self, event):
        EpyGlob.IgnoreEvents = True
        if not event.CanVeto():   
               return 
               
        self.OnCloseAll(None)       
        
        event.Skip()

    #**********************************************************************************
    def OnNewFile(self, event):
        self.docMgr.NewDoc()
        
    def OnOpenFile(self, event):
        #dlg = drFileDialog.FileDialog(self, "Open", config.prefs.wildcard, MultipleSelection=True, ShowRecentFiles=True)
        dlg = wx.FileDialog(self, u"打开文件", wildcard = u"Python 文件(*.py;*.pyw)|*.py;*.pyw|所有文件 (*.*)|*.*")
        dlg.SetDirectory(EpyGlob.CurrDir)
            
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            filenames = map(lambda x: x.replace("\\", '/'), filenames)

            for fname in filenames:
                self.docMgr.OpenOrSwitchToFile(fname)
                self.UpdateRecentFiles()
        dlg.Destroy()

    def OnOpenHistory(self,event) :
        menu = wx.Menu()
        x = 0
        numfiles = len(EpyGlob.RecentFiles)
        while x < numfiles:
            menu.Append(self.ID_RECENT_FILES_BASE+x, EpyGlob.RecentFiles[x])
            self.Bind(wx.EVT_MENU,  self.OnOpenRecentFile, id=self.ID_RECENT_FILES_BASE+x)
            x = x + 1
        
        self.PopupMenu(menu, (50,50))
        
    def OnOpenRecentFile(self, event):
        recentmenuindex = event.GetId() - self.ID_RECENT_FILES_BASE
        filename = EpyGlob.RecentFiles[recentmenuindex]
        
        if not os.path.isfile(filename) :
            utils.ShowMessage(u"历史文件[%s]已经不存在!" % filename , "EasyPython Error")
            #TODO： clear recent files
            return
        
        self.docMgr.OpenOrSwitchToFile(filename)

    def OnSaveFile(self, event):
        if not self.docMgr.currDoc :
                return
        if not self.docMgr.currDoc.filename:
            return self.OnSaveAs(event)
        else:
            self.docMgr.SaveFile()
        return True

    def OnSaveAs(self, event):
        if not self.docMgr.currDoc :
                return
        
        #dlg = drFileDialog.FileDialog(self, "Save File As", config.prefs.wildcard, IsASaveDialog=True)
        dlg = wx.FileDialog(self, u"文件另存为", wildcard = u"Python 文件(*.py;*.pyw)|*.py;*.pyw|所有文件 (*.×)|*.×", style = wx.FD_SAVE)
        
        dlg.SetDirectory(EpyGlob.CurrDir)
        
        if dlg.ShowModal() != wx.ID_OK:
            return False 
            
        if not self.docMgr.SaveFile(dlg.GetPath().replace("\\", "/")):
            return False
        
        dlg.Destroy()
        
        #self.UpdateMenuAndToolbar()
        self.UpdateTitle()
        
        self.UpdateRecentFiles()
      
        return True
        
    #**********************************************************************************
    def OnSaveAll(self, event):
        if self.docMgr.GetDocCount() == 0:
            return False
    
        oldpos = self.docMgr.selection
        
        i = 0
        for doc in self.docMgr.docs :
            if doc.GetModify():
                self.docMgr.SelectDoc(i)
                self.OnSaveFile(None)
            i += 1
            
        self.docMgr.SelectDoc(oldpos)

        return True

    def OnCloseFile(self, event):
        if not self.docMgr.currDoc:
            return
        
        if self.docMgr.currDoc.GetModify():
                if utils.Ask(u'你需要保存"%s"吗?' % self.docMgr.currDoc.GetFileName(), "EasyPython"):
                    self.OnSaveFile(event)
                
        self.docMgr.CloseDoc()
    
    def OnCloseAll(self, event):
        self.PromptSaveAll()
        self.docMgr.CloseAll()
        
    def OnCloseAllOthers(self, event):
        self.PromptSaveAll(Others = True)
        self.docMgr.CloseAll(Others = True)
        
    def OnPrintFile(self, event):
        if not self.docMgr.currDoc :
                return
        self.Printer.Print(self.docMgr.currDoc.GetText(), self.docMgr.currDoc.filename, 1)
        
    #**********************************************************************************
    def OnEventFileNew(self, event) :
        pass
    
    def OnEventFileClosed(self, event) :
        pass
    
    def OnEventDocChanged(self, event) :
        pass
        
    #**********************************************************************************
    def OnCheckSyntax(self, event):
        if self.docMgr.selection < 0 :
                return
        if self.docMgr.currDoc.CheckSyntax(self.docMgr.selection):
            self.SetStatusText(u'语法检查通过', 2)

    def OnRun(self, event):
        if self.docMgr.selection < 0 :
                return
        #patch [ 1367222 ] Improved Run Command + HTML Browser
        if self.docMgr.currDoc.GetModify():
            if not utils.Ask(u"文件已经被修改了,必须保存后才能运行.\n你需要保存文件吗?", "EasyPython"):
                return
            if not self.OnSaveFile(event):
                return
            
        if not utils.IsPythonFile(self.docMgr.currDoc.filename):
                return
                
        cwd = os.getcwd()
        
        cdir, filen = os.path.split(self.docMgr.currDoc.filename)
        try:
            os.chdir(cdir)
        except:
            utils.ShowMessage(u"不能转换当前工作目录到:%s." % cdir, u"EasyPython运行错误")
            return
            
        largs = ""
        if (len(EpyGlob.LastProgArgs) > 0):
                largs = ' ' + EpyGlob.LastProgArgs
                
        if config.PLATFORM_IS_WIN:
                self.RunCmd(("cmd /k " + config.pythexecw + ' "' +
                         self.docMgr.currDoc.filename.replace("\\", "/") + '"' + largs),
                         "Running " + filen, filen)
        else:
                self.RunCmd((config.pythexec + " -u " +  config.prefs.pythonargs + ' "' + self.docMgr.currDoc.filename + '"'  + largs), 
                        "Running " + filen, filen)                #patch: [ 1366679 ] Goto Line Should Not Display At Top Of Window
        os.chdir(cwd)

    def OnSetArgs(self, event):
        d = wx.TextEntryDialog(self, "Arguments:", "EasyPython - Set Arguments", EpyGlob.LastProgArgs)
        if d.ShowModal() == wx.ID_OK:
            EpyGlob.LastProgArgs = d.GetValue()
        d.Destroy()

    def OnEnd(self, event):
        if self.pid != -1:
            wx.Process_Kill(self.pid, wx.SIGKILL)
        self.pid = -1
        
    #**********************************************************************************
    def OnPrefs(self, event):
        from drPrefsDialog import drPrefsDialog
        d = drPrefsDialog(self, -1, "EasyPython - Preferences")
        d.ShowModal()
        d.Destroy()
        
    #**********************************************************************************
    def OnToggleSourceBrowser(self, event):
        pane = self._mgr.GetPane('source_browser')    
        if pane.IsShown() :
                pane.Show(False)
        else :
                pane.Show(True)
        self._mgr.Update()
        
    #**********************************************************************************
    def OnSourceBrowserGoTo(self, event):
        drSourceBrowserGoTo.SourceBrowserGoTo(self, self.docMgr.currDoc)

    def OnSyntaxHighlightingPython(self, event):
        self.docMgr.currDoc.filetype = EpyGlob.PYTHON_FILE
        self.docMgr.currDoc.SetupPrefsDocument()

    def OnSyntaxHighlightingHTML(self, event):
        self.docMgr.currDoc.filetype = EpyGlob.HTML_FILE
        self.docMgr.currDoc.SetupPrefsDocument()

    def OnSyntaxHighlightingText(self, event):
        self.docMgr.currDoc.filetype = EpyGlob.TEXT_FILE
        self.docMgr.currDoc.SetupPrefsDocument()

    def OnToggleViewWhiteSpace(self, event):
        if not self.docMgr.currDoc :
                return
        c = self.docMgr.currDoc.GetViewWhiteSpace()
        self.docMgr.currDoc.SetViewWhiteSpace(not c)
        if config.prefs.vieweol:
                self.docMgr.currDoc.SetViewEOL(not c)

    #**********************************************************************************
    def OnCleanUpSpaces(self, event):
        wx.BeginBusyCursor()
        self.docMgr.currDoc.SetToSpaces(8)
        self.docMgr.currDoc.OnModified(None)
        wx.EndBusyCursor()
    
    def OnCommentRegion(self, event):
        self.docMgr.currDoc.CommentRegion()
    
    def OnUnCommentRegion(self, event):
        self.docMgr.currDoc.UnCommentRegion()
            
    def OnIndentRegion(self, event):
        self.docMgr.currDoc.IndentRegion()
        
    def OnDedentRegion(self, event):
        self.docMgr.currDoc.DedentRegion()
            
    #**********************************************************************************
    def OnFind(self, event):
        stc = self.docMgr.GetCurrDoc()
        d = drFindReplaceDialog(self, -1, "Find", stc)
        
        #d.SetOptions(self.FindOptions)

        if stc.GetSelectionStart() < stc.GetSelectionEnd():
            d.SetFindString(stc.GetSelectedText())
        elif config.prefs.findreplaceundercursor:
            pos = stc.GetCurrentPos()
            d.SetFindString(stc.GetTextRange(stc.WordStartPosition(pos, 1), stc.WordEndPosition(pos, 1)))
        d.Show(True)

    def OnFindNext(self, event):
        self.docMgr.GetCurrDoc().Finder.DoFindNext()

    def OnFindPrevious(self, event):
        self.docMgr.GetCurrDoc().Finder.DoFindPrevious()

    def OnReplace(self, event):
        stc = self.docMgr.GetCurrDoc()
        d = drFindReplaceDialog(self, -1, "Replace", stc, 1)
        d.SetOptions(EpyGlob.ReplaceOptions)
        if stc.GetSelectionStart() < stc.GetSelectionEnd():
            d.SetFindString(stc.GetTextRange(stc.GetSelectionStart(), stc.GetSelectionEnd()))
        else:
            d.SetFindString(stc.Finder.GetFindText())
        d.Show(True)

    def OnSelectAll(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.SelectAll()
        else:
            self.docMgr.currDoc.SelectAll()

    def OnCut(self, event):
        if not self.docMgr.currDoc :
                return
        self.docMgr.currDoc.CmdKeyExecute(wx.stc.STC_CMD_CUT)
        
    def OnCopy(self, event):
        if not self.docMgr.currDoc :
                return
        self.docMgr.currDoc.CmdKeyExecute(wx.stc.STC_CMD_COPY)
        
    def OnPaste(self, event):
        if not self.docMgr.currDoc :
                return
        self.docMgr.currDoc.Paste()
        
    def OnDelete(self, event):
        if not self.docMgr.currDoc :
                return
        self.docMgr.currDoc.CmdKeyExecute(wx.stc.STC_CMD_CLEAR)
    
    def OnUndo(self, event):
        if not self.docMgr.currDoc :
                return
        self.docMgr.currDoc.Undo()

    def OnRedo(self, event):
        if not self.docMgr.currDoc :
                return
        self.docMgr.currDoc.Redo()
                    
    #**********************************************************************************
    def OnViewAbout(self, event):
        import drAboutDialog
        drAboutDialog.Show(self)

    def OnViewHelp(self, event):
        self.ViewURLInBrowser(config.AppDir + "/documentation/help.html")
        
    #**********************************************************************************
    def UpdateRecentFiles(self) :
        #Update Recent Files
        if EpyGlob.RecentFiles.count(self.docMgr.currDoc.filename) != 0:
            EpyGlob.RecentFiles.remove(self.docMgr.currDoc.filename)
        if len(EpyGlob.RecentFiles) == config.prefs.recentfileslimit:
            EpyGlob.RecentFiles.pop()
        EpyGlob.RecentFiles.insert(0, self.docMgr.currDoc.filename)
        EpyGlob.WriteRecentFiles()
    
    def UpdateSourceBrwser(self) :
        self.SourceBrowser.Browse()
          
    #**********************************************************************************
    '''
    def OnPython(self, event):
        if config.PLATFORM_IS_WIN:        
            import win32process
            self.handle = win32process.CreateProcess(config.pythexec,
                    config.pythexec, None, None, 0,
                    win32process.CREATE_NEW_CONSOLE, 
                    None , 
                    None,
                    win32process.STARTUPINFO()
                    )
        elif config.PLATFORM_IS_GTK :
            p = subprocess.Popen([config.pythexec],shell=True)
        else :
            pass
    '''
    def Execute(self, command, statustext = ''):
        if not statustext:
            statustext = "Running Command"
        self.RunCmd(command, statustext, command)
    
    def OnPython(self, event) : #ExecutePython(self):
        self.txtPrompt.pythonintepreter = 1
        self.ExecuteWithPython('', 'Running Python Interpreter', '-i', 'Python')
        try:
            wx.Yield()
        except:
            pass
        #workaround by Dunderhead.
        #if self.PLATFORM_IS_WIN:
        #self.txtPrompt._waitforoutput('>>>')
        #self.txtPrompt._waitforoutput('>>>')
        #self.txtPrompt.ExecuteCommands(self.prefs.promptstartupscript)

    def ExecuteWithPython(self, command = '', statustext = '', pythonargs='', pagetext='Python'):
        commandstring = string.join([' -u',  command], ' ').rstrip()
        #if self.PLATFORM_IS_WIN:
        self.RunCmd(('python.exe ' + commandstring), statustext, pagetext)
        #else:
        #    self.RunCmd((self.pythexec + commandstring), statustext, pagetext)
           
    def RunCmd(self, command, statustext = "Running Command", pagetext="Prompt", redin="", redout = "", rederr=""):        
        '''
        process = wx.Process(self) 
        
        if type(command) == unicode:
                command = command.encode(wx.GetDefaultPyEncoding())
    
        wx.Execute(command, wx.EXEC_ASYNC , process)
        '''
        self.txtPrompt.SetReadOnly(0)
        self.txtPrompt.SetText(command + '\n')
        self.txtPrompt.SetScrollWidth(1)
        self.txtPrompt.editpoint = self.txtPrompt.GetLength()
        self.txtPrompt.GotoPos(self.txtPrompt.editpoint)
        self.SetStatusText(statustext, 2)
        self.txtPrompt.process = wx.Process(self)
        self.txtPrompt.process.Redirect()
        self.txtPrompt.pid = wx.Execute(command, wx.EXEC_ASYNC | wx.EXEC_NOHIDE, self.txtPrompt.process)
        '''
        if self.PLATFORM_IS_WIN:
            self.txtPrompt.pid = wx.Execute(command, wx.EXEC_ASYNC | wx.EXEC_NOHIDE, self.txtPrompt.process)
        else:
            self.txtPrompt.pid = wx.Execute(command, wx.EXEC_ASYNC, self.txtPrompt.process)
        '''
        self.txtPrompt.inputstream = self.txtPrompt.process.GetInputStream()
        self.txtPrompt.errorstream = self.txtPrompt.process.GetErrorStream()
        self.txtPrompt.outputstream = self.txtPrompt.process.GetOutputStream()

        self.txtPrompt.process.redirectOut = redout
        self.txtPrompt.process.redirectErr = rederr

        self.txtPrompt.SetFocus()

        
    #********************************************************************************** 
    def RunShortcuts(self, event, stc = None, SplitView = 0):
        #return drShortcuts.RunShortcuts(EpyGlob.shortcutMgr, event, stc, SplitView)
        pass
        
    #**********************************************************************************  
    def updatePrefs(self, oldprefs):
        #Styling:
        
        for document in self.docMgr.docs:
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
            EpyGlob.FindOptions = []
            EpyGlob.ReplaceOptions = []

        if not (oldprefs.recentfileslimit == config.prefs.recentfileslimit):
            self.DestroyRecentFileMenu()
            EpyGlob.RecentFiles = []

            self.LoadRecentFiles()
            self.CreateRecentFileMenu()

        #Styling:
        self.docMgr.currDoc.StyleResetDefault()
        self.docMgr.currDoc.StyleClearAll()

        self.txtPrompt.StyleResetDefault()
        self.txtPrompt.StyleClearAll()

        self.docMgr.currDoc.SetupPrefsDocument(0)
        if self.docMgr.currDoc.GetViewWhiteSpace():
            self.docMgr.currDoc.SetViewEOL(config.prefs.vieweol)
        self.txtPrompt.SetupPrefsPrompt(0)
        if self.txtPrompt.GetViewWhiteSpace():
            self.txtPrompt.SetViewEOL(config.prefs.vieweol)

        if oldprefs.docfolding[self.docMgr.currDoc.filetype]:
            if not config.prefs.docfolding[self.docMgr.currDoc.filetype]:
                self.docMgr.currDoc.FoldAll(True)

        self.docMgr.currDoc.OnModified(None)
        self.docMgr.currDoc.OnPositionChanged(None)

        #Parenthesis Matching:
        if oldprefs.docparenthesismatching != config.prefs.docparenthesismatching:
            if not config.prefs.docparenthesismatching:
                #Clear Parenthesis Highlighting
                self.docMgr.currDoc.BraceBadLight(wx.stc.STC_INVALID_POSITION)
                self.docMgr.currDoc.BraceHighlight(wx.stc.STC_INVALID_POSITION, wx.stc.STC_INVALID_POSITION)

    def ViewURLInBrowser(self, url):
        if url.find('http:') == -1:
            url = os.path.normpath(url)
        if config.prefs.documentationbrowser == '<os.startfile>' and config.PLATFORM_IS_WIN:
            os.startfile(url)
            return
        wx.Execute((config.prefs.documentationbrowser + ' "' + url + '"'), wx.EXEC_ASYNC)

    #**********************************************************************************
    def GetPreference(self, pref, key=None):
        if key is not None:
            return config.prefs[pref][key]
        else:
            return config.prefs[pref]
    
    def UpdateTitle(self) :
        title = "EasyPython"
        
        if self.docMgr.currDoc :
            title += " - " + self.docMgr.currDoc.GetFileNameTitleFull()
        
        self.SetTitle(title)
   
    def PromptSaveAll(self, Others = False) :   
        if self.docMgr.GetDocCount() == 0:
            return
    
        oldpos = self.docMgr.selection
        
        tosaveArray = []
        tosaveLabels = []
        
        i = 0
        for doc in self.docMgr.docs:
            tosaveLabels.append(doc.GetFileNameTitle())
            if doc.GetModify():
                tosaveArray.append(i)
            i += 1
        
        if len(tosaveArray) == 0 :
            return
            
        d = wx.lib.dialogs.MultipleChoiceDialog(self, u"需要保存这些文件吗?", u"保存", tosaveLabels, size=(300, 300))
        
        l = len(tosaveArray)
        y = 0
        while y < l:
            d.lbox.SetSelection(y)
            y += 1
            
        answer = d.ShowModal()
        selections = d.GetValue()
        d.Destroy()
        
        if answer != wx.ID_OK:
            return False
            
        for selection in selections:
                self.docMgr.SelectDoc(selection)
                self.OnSaveFile(None)
                
        self.docMgr.SelectDoc(oldpos)

        return True
              
    
#*******************************************************************************************************
class SplashScreen(wx.SplashScreen):
    def __init__(self, app):
        self.app = app
        bmp = wx.Image(os.path.join(config.BitmapDir,"splash.png")).ConvertToBitmap()
        wx.SplashScreen.__init__(self, bmp,
                                 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                 2500, None, -1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.fc = wx.FutureCall(1500, app.ShowMain)

    def OnClose(self, evt):
        # Make sure the default handler runs too so this window gets
        # destroyed
        evt.Skip()
        self.Hide()
        
        # if the timer is still running then go ahead and show the
        # main frame now
        if self.fc.IsRunning():
            self.fc.Stop()
            
    
#*******************************************************************************************************
class EasyPythonApp(wx.App):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        sys.excepthook = self.__ExceptHook__
        
        use_stdout_window = 0
        if kwargs.has_key('use_stdout_window'):
            use_stdout_window = kwargs['use_stdout_window']
            del kwargs['use_stdout_window']
        wx.App.__init__(self, use_stdout_window)

    def OnInit(self):       
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        
        config.Init()
         
        splash = SplashScreen(self)
        splash.Show()

        return True
    
    def ShowMain(self) :
        self.mainFrame = MainFrame()
        self.mainFrame.Show()
        self.SetTopWindow(self.mainFrame)
        
    def OnActivate(self, event):
        if event.GetActive():
            self.mainFrame.OnActivate()
        event.Skip()
    
    def Run(self):
        self.MainLoop()
        self.Unbind(wx.EVT_ACTIVATE_APP) # needed for wxpython 2.9, else deadobject error, because of delivering event
    
    def __ExceptHook__(self, exctype, value, tb):
        s = ''.join(traceback.format_exception(exctype, value, tb))
        dlg = wx.lib.dialogs.ScrolledMessageDialog(None, s, u"出错信息")
        dlg.ShowModal()
        dlg.Destroy()

#*******************************************************************************************************
def main():
    try:
        demoPath = os.path.dirname(__file__)
        os.chdir(demoPath)
    except: pass
        
    app = EasyPythonApp(False)
    app.Run()
    
#*******************************************************************************************************
if __name__ == '__main__':
    main()
