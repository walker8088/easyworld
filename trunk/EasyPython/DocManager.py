
#coding:utf-8
import os, re, shutil
import wx

import drTabNanny
#from drNotebook import *
from drText import DrText
import drEncoding

import EventManager

import config, EpyGlob
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
                EpyGlob.CurrDir = os.path.split(self.currDoc.filename)[0]
 
        self.UpdateTitle()
        
        if lastDoc :
            self.currDoc.Finder.Copy(oldfinder)
            #set from prev eol and whitespace state
            #flicker
            if self.currDoc.GetViewEOL() != prev_vieweol:
                self.currDoc.SetViewEOL(prev_vieweol)
            self.currDoc.SetViewWhiteSpace(prev_viewwhitespace)

        self.frame.UpdateSourceBrwser()
       
        EpyGlob.EventMgr.PostSelectChangedEvent(self.currDoc, index)
    
    def NewDoc(self) :
        last = self.GetLastDocNo()
        
        newDoc = DrText(self.frame)
        newDoc.untitlednumber = last
        newDoc.filetype = EpyGlob.PYTHON_FILE
        #newDoc.filename = None
        newDoc.IsActive = False
        newDoc.SetupPrefsDocument(0)
        newDoc.SetSTCFocus(True)
        
        self.docs.append(newDoc)
        self.docbook.AddPage(newDoc, newDoc.GetFileNameTitle())
                
        EpyGlob.EventMgr.PostFileNewEvent(newDoc)
        
        self.SelectDoc(len(self.docs)-1)

    def CloseDoc(self) :    
        doc  = self.currDoc
        #EpyGlob.EventMgr.PostFileClosingEvent(doc)
       
        self.docs.remove(doc)
        
        EpyGlob.EventMgr.PostFileClosedEvent(doc)
        
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
        filename = os.path.abspath(filename).replace("\\", '/')

        if type(filename) != unicode:
            filename = filename.decode(wx.GetDefaultPyEncoding())
        
        if not os.path.isfile(filename) :
            utils.ShowMessage(u"文件[%s]不存在!" % filename , "EasyPython Error")
            return
        
        wx.BeginBusyCursor()
   
        encoding='utf-8'    
         
        try:     
            cfile = file(filename, 'rb')
        except:
            utils.ShowMessage("Error Opening: " + filename , "EasyPython Error")
            wx.EndBusyCursor()
            return
        
        '''    
        if editrecentfiles:
            self.DestroyRecentFileMenu()
            if EpyGlob.RecentFiles.count(filename) != 0:
                EpyGlob.RecentFiles.remove(filename)
            if len(EpyGlob.RecentFiles) == config.prefs.recentfileslimit:
                EpyGlob.RecentFiles.pop()
            EpyGlob.RecentFiles.insert(0, filename)
            self.WriteRecentFiles()
        '''
        
        if oldDoc != None :
            newDoc = oldDoc
        else :    
            newDoc = DrText(self.frame)
            newDoc.filename = filename
            newDoc.untitlednumber = -1
        
            self.docs.append(newDoc)
            EpyGlob.EventMgr.PostFileLoadingEvent(newDoc)
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
                self.frame.OnCloseFile(None)
                return
            
            cfile.close()
            
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
        
        EpyGlob.EventMgr.PostFileLoadedEvent(newDoc)
       
        wx.EndBusyCursor()
        
    def SaveFile(self, SaveAsName = None):
        
        doc = self.currDoc
        
        
        if SaveAsName :
            oldname = doc.filename
            doc.filename = SaveAsName
            
        EpyGlob.EventMgr.PostFileSavingEvent(doc)
        
        if os.path.exists(doc.filename) and (not os.access(doc.filename, os.W_OK)):
            utils.ShowMessage(u'写入文件: "%s" 时发生错误, 请检查文件权限问题。' % (doc.filename), u'保存错误')
            
            if SaveAsName :
                doc.filename = oldname
            
            return False
            
        try:
            #if os.path.exists(doc.filename) :
            #    try:
            #        shutil.copyfile(doc.filename, doc.filename + ".bak")
            #    except:
            #        utils.ShowMessage((u"备份文件到: " + doc.filename + ".bak 发生错误"),  u'保存错误')

            encoding = doc.GetEncoding()
            doc.RemoveTrailingWhitespace()
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
        
        EpyGlob.CurrDir = os.path.dirname(doc.filename)
           
        EpyGlob.EventMgr.PostFileSavedEvent(doc)
       
        return True
    
    #**********************************************************************************
    
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
            
    def UpdateDocs(self) :    
        for doc in self.docs:
            if not doc.filename:
                continue
            if not os.path.exists(doc.filename): 
                #TODO：文件删除处理
                continue
            current_mtime = int(os.stat(doc.filename).st_mtime)
            if current_mtime != doc.mtime:
                if utils.Ask(u'文件"%s"已经被修改了.要重新载入吗?' % (doc.filename), "Reload File?"):
                    self.OpenFile(doc.filename, doc)
                doc.mtime = current_mtime
                
    def UpdateTitle(self) :
        if self.currDoc :
            self.frame.SetTitle("EasyPython - " + self.currDoc.GetFileNameTitleFull())
            self.docbook.SetPageText(self.selection, self.currDoc.GetFileNameTitle())
        else :
            self.frame.SetTitle("EasyPython")
            
    #**********************************************************************************
            
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
    
