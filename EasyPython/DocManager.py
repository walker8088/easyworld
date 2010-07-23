
#coding:utf-8
import os, re, shutil
import wx

import drTabNanny
#from drNotebook import *
from drText import DrText
import drEncoding

import EventManager

import config, glob
import utils

class DocManager() :
    def __init__(self, frame, docbook):
        
        self.frame = frame
        self.docbook = docbook
                
        #Regex Line Endings:
        self.relewin = re.compile('\r\n', re.M)
        self.releunix = re.compile('[^\r]\n', re.M)
        self.relemac = re.compile('\re[^\n]', re.M)
        
        #Constant messages for file format checking.
        self.FFMESSAGE = ["Unix Mode ('\\n')", "DOS/Windows Mode ('\\r\\n')", "Mac Mode ('\\r')"]
        self.TABMESSAGE = ['Spaces', 'Mixed', 'Tabs', 'None']

        self.RecheckSyntax = re.compile('line \d+', re.M)

        self.docs = []
        self.prompts = []
        
        self.selection = -1
        self.currDoc = None
        
        self.docbook.SetDocManager(self)
    
    def GetDocCount(self) :
        return len(self.docs)
        
    def SelectDoc(self, index) :        
        print "SelectDoc:", index
            
        lastDoc = None    
        if self.currDoc  :
            lastDoc = self.currDoc
            self.currDoc.IsActive = False
            self.currDoc.OnModified(None)
        
            oldfinder = self.currDoc.Finder
    
            #save show eol and whitespace state
            try:
                prev_vieweol = self.currDoc.GetViewEOL()
                prev_viewwhitespace = self.currDoc.GetViewWhiteSpace()
            except:
                prev_vieweol = False
                prev_viewwhitespace = False
            
        self.selection = index
        self.currDoc = self.docs[self.selection]
        self.docbook.SetSelection(index)

        self.currDoc.IsActive = True
        self.currDoc.OnModified(None)
        self.currDoc.SetFocus()
        if self.currDoc.filename:
                glob.CurrDir = os.path.split(self.currDoc.filename)[0]
 
        self.UpdateTitle()
        
        self.UpdateHighLightMenu()
        
        if lastDoc :
            self.currDoc.Finder.Copy(oldfinder)
            #set from prev eol and whitespace state
            #flicker
            if self.currDoc.GetViewEOL() != prev_vieweol:
                self.currDoc.SetViewEOL(prev_vieweol)
            self.currDoc.SetViewWhiteSpace(prev_viewwhitespace)

        self.frame.UpdateSourceBrwser()
       
        glob.EventMgr.PostSelectChangedEvent(self.currDoc, index)
    
    def NewDoc(self) :
        last = self.GetLastDocNo()
        
        newDoc = DrText(self.frame)
        newDoc.untitlednumber = last
        newDoc.filetype = glob.PYTHON_FILE
        #newDoc.filename = None
        newDoc.IsActive = False
        newDoc.SetupPrefsDocument(0)
        newDoc.SetSTCFocus(True)
        
        self.docs.append(newDoc)
        self.docbook.AddPage(newDoc, newDoc.GetFileNameTitle())
                
        glob.EventMgr.PostFileNewEvent(newDoc)
        
        self.SelectDoc(len(self.docs)-1)

    def CloseDoc(self) :    
    
        doc  = self.currDoc
        glob.EventMgr.PostFileClosingEvent(doc)
       
        self.docs.remove(doc)
        
        glob.EventMgr.PostFileClosedEvent(doc)
        
        self.currDoc = None
        self.selection = -1
       
    def CloseAll(self, Others = False) :
        docIndex = 0
        for doc in xrange(len(self.docs)) :
            if Others and index == self.select :
                docIndex = 1
                continue
            self.SelectDoc(docIndex)
            self.CloseDoc()    
        
    #**********************************************************************************
    def GetOpened(self):
        def _get_filename(x):
            return x.filename.lower()
        return map(_get_filename, self.docs)

    def OpenOrSwitchToFile(self, filename):
        filename = filename.replace("\\", "/")
        alreadyopen = self.GetOpened()

        if filename.lower() in alreadyopen:
            self.SelectDoc(alreadyopen.index(filename.lower()))
            return

        self.OpenFile(filename)
        
    def OpenFile(self, filename, oldDoc = None):
    
        encoding='utf-8'    
        
        wx.BeginBusyCursor()
        
        filename = os.path.abspath(filename).replace("\\", '/')
        
        try:
            if type(filename) != unicode:
                filename = filename.decode(wx.GetDefaultPyEncoding())
                
            cfile = file(filename, 'rb')
        except:
            utils.ShowMessage("Error Opening: " + filename , "EasyPython Error")
            wx.EndBusyCursor()
            return
        
        '''    
        if editrecentfiles:
            self.DestroyRecentFileMenu()
            if glob.RecentFiles.count(filename) != 0:
                glob.RecentFiles.remove(filename)
            if len(glob.RecentFiles) == config.prefs.recentfileslimit:
                glob.RecentFiles.pop()
            glob.RecentFiles.insert(0, filename)
            self.WriteRecentFiles()
        '''
        
        if oldDoc != None :
            newDoc = oldDoc
        else :    
            newDoc = DrText(self.frame)
            newDoc.filename = filename
            newDoc.untitlednumber = -1
        
            self.docs.append(newDoc)
            glob.EventMgr.PostFileLoadingEvent(newDoc)
            self.docbook.AddPage(newDoc, newDoc.GetFileNameTitle())
            
        try:
            oof = cfile.read()
       
            #Encoding
            try:
                oof, e = drEncoding.EncodeText(oof, encoding, True)
                newDoc.SetText(oof)
                newDoc.SetEncoding(e)
            except:
                utils.ShowMessage('There was an error opening the document %s.' % (filename), 'Open Error')
                wx.EndBusyCursor()
                self.frame.OnClose(None)
                return
            
            cfile.close()
            
            if utils.IsPythonFile(filename):
                #Python
                newDoc.filetype = glob.PYTHON_FILE
                self.frame.HightLightMenu.Check(self.frame.ID_HIGHLIGHT_PYTHON, True)
            elif utils.IsHtmlFile(filename):
                #HTML
                newDoc.filetype = glob.HTML_FILE
                self.frame.HightLightMenu.Check(self.frame.ID_HIGHLIGHT_HTML, True)
            else:
                #Default
                newDoc.filetype = glob.TEXT_FILE
                self.frame.HightLightMenu.Check(self.frame.ID_HIGHLIGHT_PLAIN_TEXT, True)
            
            newDoc.EmptyUndoBuffer()
            newDoc.SetSavePoint()
            newDoc.SetupPrefsDocument()
            newDoc.SetupLineNumbersMargin()
            newDoc.indentationtype = newDoc.CheckIndentation()
            self.CheckIndentation(newDoc, oof)
            newDoc.mtime = int(os.stat(filename).st_mtime)
            newDoc.SetScrollWidth(1)
            self.CheckLineEnding(newDoc, oof)
            
            #Scrolling
            lines = oof.split(newDoc.GetEndOfLineCharacter())

            spaces = "\t".expandtabs(config.prefs.doctabwidth[newDoc.filetype])

            line = ''
            length = 0
            x = 0
            for l in lines:
                if len(l) > length:
                    line = l
                    length = len(l)
                x += 1

            line = line.replace('\t', spaces) + '000'

            scrollwidth = newDoc.TextWidth(wx.stc.STC_STYLE_DEFAULT, line)

            newDoc.SetScrollWidth(scrollwidth)

            newDoc.SetXOffset(0)
            #/End Scrolling

        except:
            utils.ShowMessage("Error Opening: " + filename + "Processing failed" , "EasyPython Error")

        #self.frame.CreateRecentFileMenu()
        index = self.docs.index(newDoc)
        self.SelectDoc(index)
        
        glob.EventMgr.PostFileLoadedEvent(newDoc)
       
        wx.EndBusyCursor()
        
    def SaveFile(self, SaveAsName = None):
        
        doc = self.currDoc
        
        
        if SaveAsName :
            oldname = doc.filename
            doc.filename = SaveAsName
            
        glob.EventMgr.PostFileSavingEvent(doc)
        
        if os.path.exists(doc.filename) and (not os.access(doc.filename, os.W_OK)):
            utils.ShowMessage(u'写入文件: "%s" 时发生错误, 请检查文件权限问题。' % (doc.filename), u'保存错误')
            
            if SaveAsName :
                doc.filename = oldname
            
            return False
            
        try:
            try:
                shutil.copyfile(doc.filename, doc.filename + ".bak")
            except:
                utils.ShowMessage((u"备份文件到: " + doc.filename + ".bak 发生错误"),  u'保存错误')

            encoding = doc.GetEncoding()

            self.RemoveTrailingWhitespace()

            ctext = drEncoding.DecodeText(doc.GetText(), encoding)

            cfile = file(doc.filename, 'wb')
            cfile.write(ctext)
            cfile.close()

            #Save Stat Info:
            doc.mtime = int(os.stat(doc.filename).st_mtime)
            
        except:
            utils.ShowMessage(("写入文件错误: " + doc.filename), u'保存错误')
            
            if SaveAsName :
                doc.filename = oldname
            
            return False
        
        if doc.untitlednumber > 0:
            doc.untitlednumber = -1
            
        doc.SetSavePoint()
        doc.OnModified(None)
        
        doc.SetupPrefsDocument()
        
        glob.CurrDir = os.path.dirname(doc.filename)
        
        self.UpdateHighLightMenu()
        
        glob.EventMgr.PostFileSavedEvent(doc)
       
        return True
    
    #**********************************************************************************
    def UpdateDocs(self) :    
        for Document in self.docs:
            if not Document.filename:
                continue
            if not os.path.exists(Document.filename): #bug 2010127 reported by by Luca Falavigna - dktrkranz, thanks
                continue
            current_mtime = int(os.stat(Document.filename).st_mtime)
            if current_mtime != Document.mtime:
                if utils.Ask(u'文件"%s"已经被修改了.要重新载入吗?' % (Document.filename), "Reload File?"):
                    self.OpenFile(Document.filename, Document)
                Document.mtime = current_mtime
            
    def UpdateHighLightMenu(self) :
        if self.currDoc.filetype == glob.PYTHON_FILE:
            self.frame.HightLightMenu.Check(self.frame.ID_HIGHLIGHT_PYTHON, True)
        if self.currDoc.filetype == glob.HTML_FILE:
            self.frame.HightLightMenu.Check(self.frame.ID_HIGHLIGHT_HTML, True)
        if self.currDoc.filetype == glob.TEXT_FILE:
            self.frame.HightLightMenu.Check(self.frame.ID_HIGHLIGHT_PLAIN_TEXT, True)
    
    def UpdateTitle(self) :
        if self.currDoc :
            self.frame.SetTitle("EasyPython - " + self.currDoc.GetFileNameTitleFull())
            self.docbook.SetPageText(self.selection, self.currDoc.GetFileNameTitle())
        else :
            self.frame.SetTitle("EasyPython")
            
    #**********************************************************************************
    def RemoveTrailingWhitespace(self):
        if not config.prefs.docremovetrailingwhitespace[self.currDoc.filetype]:
                return
                
        eol = self.currDoc.GetEndOfLineCharacter()
        lines = self.currDoc.GetText().split(eol)
        new_lines = []
        nr_lines = 0
        nr_clines = 0
        regex = re.compile('\s+' + eol, re.MULTILINE)

        for line in lines:
            nr_lines += 1
            result = regex.search(line + eol)
            if result is not None:
                end = result.start()
                nr_clines += 1
                new_lines.append (line [:end])
            else:
                new_lines.append(line)

        changed = False
        if nr_clines > 0:
                changed = True
                newtext = string.join(new_lines, eol)
                #save current line
                curline = self.currDoc.GetCurrentLine()
                self.currDoc.SetText(newtext)
                #jump to saved current line
                self.currDoc.GotoLine(curline)
                self.frame.SetStatusText("Removed trailing whitespaces", 2)
        if not changed:
            self.frame.SetStatusText("", 2)

    def FormatMode(self, mode) :    
        wx.BeginBusyCursor()
        wx.Yield()
        if mode == "Mac" :
            self.currDoc.SetEOLMode(wx.stc.STC_EOL_CR)
            text = self.currDoc.GetText()
            text = glob.FormatMacReTarget.sub('\r', text)
            self.currDoc.SetText(text)
            self.currDoc.OnModified(None)
        elif mode == "Unix" :
            self.currDoc.SetEOLMode(wx.stc.STC_EOL_LF)
            text = self.currDoc.GetText()
            text = glob.FormatUnixReTarget.sub('\n', text)
            self.currDoc.SetText(text)
        elif mode == 'Win' :            
            self.currDoc.SetEOLMode(wx.stc.STC_EOL_CRLF)
            text = self.currDoc.GetText()
            text = glob.FormatWinReTarget.sub('\r\n', text)
            self.currDoc.SetText(text)
            
        self.currDoc.OnModified(None)
        wx.EndBusyCursor()
    
    def IndentRegion(self) :    
        #Submitted Patch:  Franz Steinhausler
        #Submitted Patch (ModEvent Mask), Franz Steinhausler
        beg, end = self.currDoc.GetSelection()
        begline = self.currDoc.LineFromPosition(beg)
        endline = self.currDoc.LineFromPosition(end)

        mask = self.currDoc.GetModEventMask()
        self.currDoc.SetModEventMask(0)

        if begline == endline:
            #This section modified by Dan
            pos = self.currDoc.PositionFromLine(begline)
            self.currDoc.SetSelection(pos, pos)
            self.currDoc.GotoPos(pos)
            self.currDoc.Tab()
            self.currDoc.SetSelection(pos, self.currDoc.GetLineEndPosition(begline))
            self.currDoc.SetModEventMask(mask)
            return

        #Submitted Patch:  Christian Daven
        self.currDoc.Tab()
        self.currDoc.SetModEventMask(mask)
        
    def DedentRegion(self) :    
        #Submitted Patch:  Franz Steinhausler
        #Submitted Patch (ModEvent Mask), Franz Steinhausler
        beg, end = self.currDoc.GetSelection()
        begline = self.currDoc.LineFromPosition(beg)
        endline = self.currDoc.LineFromPosition(end)

        mask = self.currDoc.GetModEventMask()
        self.currDoc.SetModEventMask(0)

        if begline == endline:
            #This section modified by Dan
            pos = self.currDoc.PositionFromLine(begline)
            self.currDoc.SetSelection(pos, pos)
            self.currDoc.GotoPos(pos)
            self.currDoc.BackTab()
            self.currDoc.SetSelection(pos, self.currDoc.GetLineEndPosition(begline))
            self.currDoc.SetModEventMask(mask)
            return

        #Submitted Patch:  Christian Daven
        self.currDoc.BackTab()
        self.currDoc.SetModEventMask(mask)

    def CenterCurrentLine(self, linenr):
        self.currDoc.EnsureVisible(linenr)
        #patch: [ 1366679 ] Goto Line Should Not Display At Top Of Window
        #self.currDoc.ScrollToLine(v)h
        top = linenr - self.currDoc.LinesOnScreen()/2
        if top < 0:
            top = 0
        self.currDoc.ScrollToLine(top)
        #self.currDoc.GotoLine(linenr)
        
    def CheckSyntax(self, docNumber=-1):
        if docNumber == -1:
            docNumber = self.selection
        fn = self.docs[docNumber].GetFileName()
        if not self.docs[docNumber].filename:
            return False
        #Check Syntax First
        try:
            encoding = self.docs[docNumber].GetEncoding()
            ctext = drEncoding.DecodeText(self.docs[docNumber].GetText(), encoding)
            ctext = ctext.replace('\r\n', '\n').replace('\r', '\n')
            compile(ctext, fn, 'exec')
        except Exception, e:
            excstr = str(e)
            result = glob.RecheckSyntax.search(excstr)
            if result is not None:
                num = result.group()[5:].strip()
                try:
                    n = int(num) - 1
                    self.SelectDoc(docNumber)
                    self.currDoc.ScrollToLine(n)
                    self.currDoc.GotoLine(n)
                    utils.ShowMessage('compile:\n' + excstr)
                    self.currDoc.SetSTCFocus(True)
                    self.currDoc.SetFocus()
                    #Stop the function here if something is found.
                    return False
                except:
                    utils.ShowMessage('Line Number Error:\n\n'+excstr, u'语法错误(Syntax Error)')
            else:
                utils.ShowMessage('No Line Number Found:\n\n' + excstr, u'语法错误(Syntax Error)')

        #Now Check Indentation
        result = drTabNanny.Check(fn)
        results = result.split()
        if len(results) > 1:
            num = results[1]
            try:
                n = int(num) - 1
                self.SelectDoc(docNumber)
                self.currDoc.ScrollToLine(n)
                self.currDoc.GotoLine(n)
                utils.ShowMessage('tabnanny:\n' + result)
                self.currDoc.SetSTCFocus(True)
                self.currDoc.SetFocus()
                return False
            except:
                utils.ShowMessage('Line Number Error:\n\n'+result, 'TabNanny Trouble')

        return True
    
    def CommentRegion(self) :    
        selstart, selend = self.currDoc.GetSelection()
        #From the start of the first line selected
        oldcursorpos = self.currDoc.GetCurrentPos()
        startline = self.currDoc.LineFromPosition(selstart)
        self.currDoc.GotoLine(startline)
        start = self.currDoc.GetCurrentPos()
        #To the end of the last line selected
        #Bugfix Chris Wilson
        #Edited by Dan (selend fix)
        if selend == selstart:
            tend = selend
        else:
            tend = selend - 1
        docstring = config.prefs.doccommentstring[self.currDoc.filetype]
        if os.path.splitext(self.currDoc.filename)[1] == ".lua":
            docstring = "--"

        end = self.currDoc.GetLineEndPosition(self.currDoc.LineFromPosition(tend))
        #End Bugfix Chris Wilson
        eol = self.currDoc.GetEndOfLineCharacter()
        corr = 0
        l = len(self.currDoc.GetText())
        if config.prefs.doccommentmode == 0:
            self.currDoc.SetSelection(start, end)
            text = docstring + self.currDoc.GetSelectedText()
            text = text.replace(eol, eol + docstring)
            self.currDoc.ReplaceSelection(text)
        else:
            mask = self.currDoc.GetModEventMask()
            self.currDoc.SetModEventMask(0)
            wpos = start
            while wpos < end:
                ws = self.currDoc.GetLineIndentPosition(startline)
                le = self.currDoc.GetLineEndPosition(startline)
                if ws != le:
                    self.currDoc.InsertText(ws, docstring)
                startline += 1
                wpos = self.currDoc.PositionFromLine(startline)
            self.currDoc.SetModEventMask(mask)
        corr = len(self.currDoc.GetText()) - l
        self.currDoc.GotoPos(oldcursorpos + corr)

    def UnCommentRegion(self) :
        #franz: pos is not used
        selstart, selend = self.currDoc.GetSelection()
        #From the start of the first line selected
        startline = self.currDoc.LineFromPosition(selstart)
        oldcursorpos = self.currDoc.GetCurrentPos()
        self.currDoc.GotoLine(startline)
        start = self.currDoc.GetCurrentPos()
        #To the end of the last line selected
        #Bugfix Chris Wilson
        #Edited by Dan (selend fix)
        if selend == selstart:
            tend = selend
        else:
            tend = selend - 1
        end = self.currDoc.GetLineEndPosition(self.currDoc.LineFromPosition(tend))
        #End Bugfix Chris Wilson

        mask = self.currDoc.GetModEventMask()
        self.currDoc.SetModEventMask(0)
        lpos = start
        newtext = ""
        l = len(self.currDoc.GetText())

        docstring = config.prefs.doccommentstring[self.currDoc.filetype]
        if os.path.splitext(self.currDoc.filename)[1] == ".lua":
            docstring = "--"

        ldocstring = len(docstring)
        while lpos < end:
            lpos = self.currDoc.PositionFromLine(startline)
            line = self.currDoc.GetLine(startline)
            lc = line.find(docstring)
            if lc > -1:
                prestyle = self.currDoc.GetStyleAt(lpos + lc - 1)
                style = self.currDoc.GetStyleAt(lpos + lc)
                if self.currDoc.filetype == 1 or os.path.splitext(self.currDoc.filename)[1] == ".lua":
                    if 0:
                        newtext += line
                    else:
                        newtext += line[0:lc] + line[lc+ldocstring:]
                else:
                    if not ((not (prestyle == wx.stc.STC_P_COMMENTLINE) and not (prestyle == wx.stc.STC_P_COMMENTBLOCK))\
                    and ((style == wx.stc.STC_P_COMMENTLINE) or (style == wx.stc.STC_P_COMMENTBLOCK))):
                        newtext += line
                    else:
                        newtext += line[0:lc] + line[lc+ldocstring:]
            else:
                newtext += line
            startline += 1
            lpos = self.currDoc.PositionFromLine(startline)
        self.currDoc.SetModEventMask(mask)
        self.currDoc.SetSelection(start, end)
        self.currDoc.ReplaceSelection(newtext.rstrip(self.currDoc.GetEndOfLineCharacter()))
        corr = len(self.currDoc.GetText()) - l
        self.currDoc.GotoPos(oldcursorpos + corr)
    
    def CheckIndentation(self, doc, oof) :   
        #Indentation
        if config.prefs.docusefileindentation:
            indentation = doc.CheckIndentation(oof)
            if config.prefs.checkindentation:
                if config.prefs.docusetabs[doc.filetype]:
                    i = 1
                else:
                    i = -1
                if (indentation != i) and (indentation != 2):
                    answer = utils.Ask((doc.filename + ' is currently '\
                        + self.TABMESSAGE[indentation+1] +
                        ".\nWould you like to change it to the default?\nThe Default is: " +
                        self.TABMESSAGE[i+1]), "Indentation Not Default")
                    if answer:
                        indentation = i
                        if i == 1:
                            doc.SetToTabs(config.prefs.doctabwidth[doc.filetype])
                        else:
                            doc.SetToSpaces(config.prefs.doctabwidth[doc.filetype])
            if indentation == -1:
                usetabs = False
            elif indentation == 1:
                usetabs = True
            else:
                usetabs = config.prefs.docusetabs[doc.filetype]
            doc.SetUseTabs(usetabs)
            doc.SetupTabs(usetabs)
    
    def CheckLineEnding(self, doc, oof) :

        doc.lineendingsaremixed = 0

        winresult = self.relewin.search(oof)
        unixresult = self.releunix.search(oof)
        macresult = self.relemac.search(oof)

        win = winresult is not None
        unix = unixresult is not None
        mac = macresult is not None

        if (win + unix + mac) > 1:
            #Which came first, unix, mac, or win?
            first = -1
            useemode = 0
            if winresult is not None:
                first = winresult.start()
                useemode = 1
            if unixresult is not None:
                if first == -1:
                    first = unixresult.start()
                else:
                    i = unixresult.start()
                    if i < first:
                        first = i
                        useemode = 0
            if macresult is not None:
                if first == -1:
                    first = macresult.start()
                else:
                    i = macresult.start()
                    if i < first:
                        first = i
                        useemode = 2
            doc.lineendingsaremixed = 1
            emodenum = useemode
        else:
            if win:
                emodenum = 1
            elif unix:
                emodenum = 0
            elif mac:
                emodenum = 2
            else:
                emodenum = config.prefs.doceolmode[doc.filetype]
            doc.lineendingsaremixed = 0

        dmodenum = config.prefs.doceolmode[doc.filetype]

        if emodenum == 1:
            emode = wx.stc.STC_EOL_CRLF
        elif emodenum == 2:
            emode = wx.stc.STC_EOL_CR
        else:
            emode = wx.stc.STC_EOL_LF
            
        doc.SetEOLMode(emode)
    
    #**********************************************************************************
    
    def GetFileName(self):
        if not self.currDoc :
            return None
        return self.currDoc.filename
            
    def GetLastDocNo(self) :            
        docCount = len(self.docs)
        unumbers = map(lambda x: x.untitlednumber, self.docs)
        unumbers.sort()
        
        x = 0
        last = 0
        while x < docCount:
            if unumbers[x] > 0:
                if unumbers[x] != (last + 1):
                    x = docCount
                else:
                    last = unumbers[x]
                    x = x + 1
            else:
                x = x + 1
        last = last + 1
        
        return last
        
    #**********************************************************************************
    