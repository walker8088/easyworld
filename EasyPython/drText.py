#coding:utf-8

#   Programmer: Daniel Pozmanter
#   E-mail:     drpython@bluebottle.com
#   Note:       You must reply to the verification e-mail to get through.
#
#   Copyright 2003-2007 Daniel Pozmanter
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   DrPython is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#Some Folding Code From demo.py by Robin Dunn
#Some more from pype by Josiah Carlson

#The Document

import os.path, re

import wx
import wx.stc

from drProperty import *
import drKeywords
import drSTC
import drEncoding

import config, EpyGlob

#*******************************************************************************************************
class DrText(drSTC.DrStyledTextControl):
    def __init__(self, parent, id = -1):
        drSTC.DrStyledTextControl.__init__(self, parent, id)
        
        self.parent = parent
        
        self.indentationtype = 1
        
        if not config.prefs.docusetabs[0]:
            self.indentationtype = -1

        self.filename = ""
        self.mtime = -1
        self.untitlednumber = 0
        self.lineendingsaremixed = 0
        self.IsActive = True
        self.filetype = 0
        self.encoding = '<Default Encoding>'
        
        self.SetupTabs()
        
        self.usestyles = (config.prefs.docusestyles == 1)
        self.indentationstring = ""

        #Keyword Search/Context Sensitive Autoindent.
        self.rekeyword = re.compile(r"(\sreturn\b)|(\sbreak\b)|(\spass\b)|(\scontinue\b)|(\sraise\b)", re.MULTILINE)
        self.reslash = re.compile(r"\\\Z")

        self.renonwhitespace = re.compile('\S', re.M)

        self.DisableShortcuts = False

        self.modified = False
        
        self.Bind(wx.EVT_UPDATE_UI,  self.OnUpdateUI, id=id)
        #self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick, id=id)
        
    def _autoindent(self):
        pos = self.GetCurrentPos()

        #Strip trailing whitespace first.
        currentline = self.LineFromPosition(pos)
        lineendpos = self.GetLineEndPosition(currentline)
        if lineendpos > pos:
            self.SetTargetStart(pos)
            self.SetTargetEnd(lineendpos)
            t = self.GetTextRange(pos, lineendpos)
            self.ReplaceTarget(t.rstrip())

        #Look at last line
        pos = pos - 1
        clinenumber = self.LineFromPosition(pos)

        linenumber = clinenumber

        self.GotoPos(pos)

        self.GotoLine(clinenumber)

        numtabs = self.GetLineIndentation(clinenumber+1) / self.tabwidth

        if self.renonwhitespace.search(self.GetLine(clinenumber+1)) is not None:
            if self.renonwhitespace.search(self.GetLine(clinenumber)) is None:
                numtabs += self.GetLineIndentation(clinenumber) / self.tabwidth

        if numtabs == 0:
            numtabs = self.GetLineIndentation(linenumber) / self.tabwidth

        if (config.prefs.docautoindent == 2) and (self.filetype == 0):
            checkat = self.GetLineEndPosition(linenumber) - 1
            if self.GetCharAt(checkat) == ord(':'):
                numtabs = numtabs + 1
            else:
                lastline = self.GetLine(linenumber)
                #Remove Comment:
                comment = lastline.find('#')
                if comment > -1:
                    lastline = lastline[:comment]
                if self.reslash.search(lastline.rstrip()) is None:
                    if self.rekeyword.search(lastline) is not None:
                        numtabs = numtabs - 1
        #Go to current line to add tabs

        self.SetTargetStart(pos+1)
        end = self.GetLineEndPosition(clinenumber+1)
        self.SetTargetEnd(end)

        self.ReplaceTarget(self.GetTextRange(pos+1, end).lstrip())

        pos = pos + 1
        self.GotoPos(pos)
        x = 0
        while x < numtabs:
            self.AddText(self.addchar)
            x = x + 1
        #/Auto Indent Code

        #Ensure proper keyboard navigation:
        self.CmdKeyExecute(wx.stc.STC_CMD_CHARLEFT)
        self.CmdKeyExecute(wx.stc.STC_CMD_CHARRIGHT)

    def CheckIndentationFor(self, type):
        text = self.GetText()
        if not text:
            return False

        if type == -1:
            return (self.respaces.search(text) is not None)
        else:
            return (self.retab.search(text) is not None)

    def EnsureVisible(self, linenumber):
        if config.prefs.docfolding[self.filetype]:
            wx.stc.StyledTextCtrl.EnsureVisible(self, linenumber)

    def GetEncoding(self):
        return self.encoding

    def SetEncoding(self, encoding):
        self.encoding = encoding

    def GetIndentationString(self):
        return self.addchar

    def GetIndentationEventText(self):
        cline, cpos = self.GetCurLine()
        nextline = self.GetLine(self.LineFromPosition(cpos)+1)

        return cline + nextline

    def GetFileName(self):
        if self.filename:
            return self.filename
        return "Program_%d.py" % self.untitlednumber

    def GetFileNameTitle(self):
        if self.filename:
            return os.path.split(self.filename)[1]
        return "Program_%d.py" % self.untitlednumber
        
    def GetFileNameTitleFull(self) :
        title = self.GetFileNameTitle()
        if self.GetModify():
            title += '[Modified]'    
        return title
        
    def OnModified(self, event):
        if EpyGlob.DisableEventHandling:
            return

        if config.prefs.sourcebrowserautorefresh:
            if EpyGlob.mainFrame.SourceBrowser is not None:
                EpyGlob.mainFrame.SourceBrowser.Browse()
        
        modify = self.GetModify()
        if (modify != self.modified) or (event is None):
            self.modified = modify
            if self.modified:
                if self.IsActive:
                    pimageidx = 3
                else:
                    pimageidx = 1
            else:
                if self.IsActive:
                    pimageidx = 2
                else:
                    pimageidx = 0
                self.SetSavePoint()

            targetPosition = EpyGlob.docMgr.docbook.GetPageIndex(self)
            EpyGlob.docMgr.docbook.SetPageImage(targetPosition, pimageidx)
            
        if config.prefs.docupdateindentation:
            #If deleting text, or undo/redo:
            if event is not None:
                modtype = event.GetModificationType()
                if (modtype & wx.stc.STC_MOD_DELETETEXT) or (modtype & wx.stc.STC_PERFORMED_UNDO) or \
                (modtype & wx.stc.STC_PERFORMED_REDO):
                    if (self.indentationtype == 0) or (self.indentationtype == 2):
                        result = self.CheckIndentation(self.GetText())
                    else:
                        hasit = self.CheckIndentationFor(self.indentationtype)
                        result = self.CheckIndentation(self.GetIndentationEventText())
                        if (result != self.indentationtype) and (result != 2):
                            result = 0
                        elif hasit:
                            result = self.indentationtype
                        else:
                            result = 2
                    self.indentationtype = result
                    self.setIndentationString()
                    return
                else:
                    result = self.CheckIndentation(self.GetIndentationEventText())
            else:
                result = self.CheckIndentation(self.GetText())

            if (result != self.indentationtype) and (result != 2):
                if (self.indentationtype == 0) or (result == 0) or \
                ((self.indentationtype + result) == 0):
                    self.indentationstring = "->MIXED"
                    result = 0
                else:
                    if result == -1:
                        self.indentationstring = "->SPACES"
                    elif result == 1:
                        self.indentationstring = "->TABS"
                self.indentationtype = result
            else:
                self.setIndentationString()
        else:
            self.indentationstring = ""

        if event is None:
            try:
                self.OnPositionChanged(None)
            except:
                pass

    def OnPositionChanged(self, event):
        if self.lineendingsaremixed:
            eolmodestr = "MIXED: "
        else:
            eolmodestr = ''
        emode = self.GetEOLMode()
        if emode == wx.stc.STC_EOL_CR:
            eolmodestr += "MAC"
        elif emode == wx.stc.STC_EOL_CRLF:
            eolmodestr += "WIN"
        else:
            eolmodestr += "UNIX"

        if self.GetOvertype():
            ovrstring = "OVR"
        else:
            ovrstring = "INS"
        statustext = "Line: %(line)s, Col: %(col)s   %(mode)s   %(ovrstring)s   %(ind)s" \
        % {"line": self.GetCurrentLine()+1, "col": self.GetColumn(self.GetCurrentPos()), \
        "mode": eolmodestr, "ovrstring": ovrstring, "ind": self.indentationstring}
        #reason gtk ; workaround tow for gtk, 15.03.2008, else segmentation fault
        #wx.CallAfter (EpyGlob.mainFrame.SetStatusText,statustext, 1)
        EpyGlob.mainFrame.SetStatusText(statustext, 1)

        if event is not None:
            event.Skip()

    def OnUpdateUI(self, event):
        if (self.usestyles) and (config.prefs.docparenthesismatching):
            #Code for parenthesis matching from wxPython Demo.
            # check for matching braces
            braceAtCaret = -1
            braceOpposite = -1
            charBefore = None
            caretPos = self.GetCurrentPos()

            if caretPos > 0:
                charBefore = self.GetCharAt(caretPos - 1)
                styleBefore = self.GetStyleAt(caretPos - 1)

            # check before
            if charBefore and chr(charBefore) in "[]{}()" and styleBefore == wx.stc.STC_P_OPERATOR:
                braceAtCaret = caretPos - 1

            # check after
            if braceAtCaret < 0:
                charAfter = self.GetCharAt(caretPos)
                styleAfter = self.GetStyleAt(caretPos)

                if charAfter and chr(charAfter) in "[]{}()" and styleAfter == wx.stc.STC_P_OPERATOR:
                    braceAtCaret = caretPos

            if braceAtCaret >= 0:
                braceOpposite = self.BraceMatch(braceAtCaret)

            if braceAtCaret != -1  and braceOpposite == -1:
                self.BraceBadLight(braceAtCaret)
            else:
                self.BraceHighlight(braceAtCaret, braceOpposite)
        event.Skip()

    def OnKeyDown(self, event):
        result = EpyGlob.mainFrame.RunShortcuts(event, self, self.DisableShortcuts)
        if result > -1:
            if (result == wx.stc.STC_CMD_NEWLINE) and (config.prefs.docautoindent):
                self._autoindent()
            if result == wx.stc.STC_CMD_TAB:
                #Check Indentation for trailing spaces
                pos = self.GetCurrentPos()

                linenumber = self.LineFromPosition(pos)
                lpos = pos - self.PositionFromLine(linenumber) - 1

                #Only at the end of a line.
                end = self.GetLineEndPosition(linenumber)
                if pos != end:
                    return

                ltext = self.GetLine(linenumber).rstrip(self.GetEndOfLineCharacter())

                #only proceed if the text up to this point is whitespace.
                if self.renonwhitespace.search(ltext[:lpos]) is not None:
                    return

                #Get the position of where the full indentation ends:
                lnws = len(ltext.rstrip())
                fiendsat = lnws + (ltext[lnws:].count(self.addchar) * len(self.addchar))

                #Get the diff betwixt this and the current pos:
                difftwixt = len(ltext) - fiendsat

                if difftwixt > 0:
                    #Check to make sure you are just looking at spaces:
                    target = ltext[fiendsat:]
                    for a in target:
                        if a != ' ':
                            return

                    #Remove the extra spaces
                    self.SetTargetStart(pos - difftwixt)
                    self.SetTargetEnd(pos)
                    self.ReplaceTarget('')
                    #/Check Indentation for trailing spaces
            elif result == wx.stc.STC_CMD_DELETEBACK:
                #if self.indentationtype == -1:
                if self.indentationtype == -1 and config.prefs.docuseintellibackspace[self.filetype]:
                    pos = self.GetCurrentPos() - 1
                    if chr(self.GetCharAt(pos)) == ' ':
                        x = 0
                        l = config.prefs.doctabwidth[self.filetype]
                        while x < l:
                            c = chr(self.GetCharAt(pos))
                            if c == ' ':
                                self.CmdKeyExecute(wx.stc.STC_CMD_DELETEBACK)
                            else:
                                x = l
                            x += 1
                            pos = pos - 1
                    else:
                        event.Skip()
                else:
                    event.Skip()

    def OnMarginClick(self, event):
        # fold and unfold as needed
        if event.GetMargin() == 2:
            lineClicked = self.LineFromPosition(event.GetPosition())
            if self.GetFoldLevel(lineClicked) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                self.ToggleFold(lineClicked)

    def setIndentationString(self):
        if self.indentationtype == 2:
            self.indentationstring = "->NONE"
        elif self.indentationtype == 1:
            self.indentationstring = "->TABS"
        elif self.indentationtype == 0:
            self.indentationstring = "->MIXED"
        elif self.indentationtype == -1:
            self.indentationstring = "->SPACES"

    def SetupLineNumbersMargin(self):
        if config.prefs.docshowlinenumbers:
            linecount = self.GetLineCount()
            if linecount < 1000:
                linecount = 1000
            lstring = str(linecount * 100)
            textwidth = self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, drEncoding.EncodeText(lstring, self.encoding))
            self.SetMarginWidth(1, textwidth)
        else:
            self.SetMarginWidth(1, 0)

    def SetupPrefsDocument(self, notmdiupdate = 1):
        if config.prefs.doconlyusedefaultsyntaxhighlighting:
            self.filetype = config.prefs.docdefaultsyntaxhighlighting
        self.SetEndAtLastLine(not config.prefs.docscrollextrapage)
        self.SetIndentationGuides(config.prefs.docuseindentationguides)
        if (len(self.filename) == 0) and not self.GetModify():
            self.SetupTabs(self.indentationtype == 1)
        if config.prefs.docfolding[self.filetype]:
            self.SetMarginWidth(2, 12)
            self.SetMarginSensitive(2, True)
            self.SetProperty("fold", "1")
        else:
            self.SetMarginWidth(2, 0)
            self.SetMarginSensitive(2, False)
            self.SetProperty("fold", "0")

        #LongLineCol from Chris McDonough

        #Adding if statement, else section myself, also added code to use line and/or background method:
        #I put the set edge color section in under styles.

        if config.prefs.doclonglinecol > 0:
            self.SetEdgeColumn(config.prefs.doclonglinecol)
            self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        elif config.prefs.doclonglinecol < 0:
            self.SetEdgeColumn(abs(config.prefs.doclonglinecol))
            self.SetEdgeMode(wx.stc.STC_EDGE_BACKGROUND)
        else:
            self.SetEdgeMode(wx.stc.STC_EDGE_NONE)

        #/LongLineCol from Chris McDonough

        self.SetupLineNumbersMargin()

        if notmdiupdate:
            self.SetViewWhiteSpace(config.prefs.docwhitespaceisvisible)
            self.SetViewEOL(config.prefs.docwhitespaceisvisible and config.prefs.vieweol)

        self.SetTabWidth(config.prefs.doctabwidth[self.filetype])

        if config.prefs.docwordwrap[self.filetype]:
            self.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            self.SetWrapMode(wx.stc.STC_WRAP_NONE)

        self.SetKeyWords(0, drKeywords.GetKeyWords(self.filetype))

        self.SetLexer(drKeywords.GetLexer(self.filetype))

        indentguide = wx.LIGHT_GREY

        if (self.filetype == EpyGlob.PYTHON_FILE) or (self.filetype == EpyGlob.TEXT_FILE):
            config.prefs.txtDocumentStyleDictionary = config.prefs.PythonStyleDictionary
            cursorstyle = config.prefs.txtDocumentStyleDictionary[15]
            foldingstyle = config.prefs.txtDocumentStyleDictionary[17]
            self.SetEdgeColour(config.prefs.txtDocumentStyleDictionary[18])
            highlightlinestyle = config.prefs.txtDocumentStyleDictionary[19]
            indentguide = config.prefs.txtDocumentStyleDictionary[20]
        elif self.filetype == EpyGlob.HTML_FILE:
            config.prefs.txtDocumentStyleDictionary = config.prefs.HTMLStyleDictionary
            cursorstyle = config.prefs.txtDocumentStyleDictionary[18]
            foldingstyle = config.prefs.txtDocumentStyleDictionary[20]
            self.SetEdgeColour(config.prefs.txtDocumentStyleDictionary[21])
            highlightlinestyle = config.prefs.txtDocumentStyleDictionary[22]

        #Folding:
        foldback = getStyleProperty("back", foldingstyle)
        foldfore = getStyleProperty("fore", foldingstyle)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND, wx.stc.STC_MARK_BOXPLUSCONNECTED, foldback, foldfore)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUSCONNECTED, foldback, foldfore)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_TCORNER, foldback, foldfore)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,wx.stc.STC_MARK_LCORNER, foldback, foldfore)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB, wx.stc.STC_MARK_VLINE, foldback, foldfore)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,wx.stc.STC_MARK_BOXPLUS, foldback, foldfore)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN,wx.stc.STC_MARK_BOXMINUS, foldback, foldfore)

        #Margin:
        self.marginbackground = foldback
        self.marginforeground = foldfore

        if config.prefs.docusestyles:

            self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, config.prefs.txtDocumentStyleDictionary[0])

            self.StyleClearAll()

            self.StartStyling(0, 0xff)

            #print cursorstyle
            #self.SetCaretForeground(cursorstyle)
            #self.SetCaretForeground("#FF0000")
            self.SetCaretForeground(cursorstyle.split(',')[0])

            if config.prefs.dochighlightcurrentline:
                self.SetCaretLineBack(highlightlinestyle)
                self.SetCaretLineVisible(True)
            else:
                self.SetCaretLineVisible(False)

            self.SetCaretWidth(config.prefs.doccaretwidth)

            self.StyleSetForeground(wx.stc.STC_STYLE_INDENTGUIDE, indentguide)

            if (config.prefs.docusestyles < 2) or (not self.filetype == EpyGlob.TEXT_FILE):
                self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, config.prefs.txtDocumentStyleDictionary[1])
                self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, config.prefs.txtDocumentStyleDictionary[2])
                self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, config.prefs.txtDocumentStyleDictionary[3])
                drKeywords.SetSTCStyles(EpyGlob.mainFrame, self, self.filetype)

    def FoldAll(self, expanding):
        lineCount = self.GetLineCount()

        #Yup, this is different from the  demo.py stuff.
        #This is a really messed up hack of the pype.py and demo.py stuff to act
        #the way I want it to...
        #Folding is just ugly.

        #Set stuff up first...
        lines = []
        #franz: lineNum not referenced
        for line in xrange(lineCount):
            lines.append(line)
        lines.reverse()

        if not expanding:
            #Code Inspired by pype.py...Wake wx.stc.STC Up Before we fold!
            self.HideLines(0, lineCount-1)
            wx.Yield()
            self.ShowLines(0, lineCount-1)

            for line in xrange(lineCount):
                if self.GetFoldLevel(line) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                    self.SetFoldExpanded(line, 1)

        #Back to demo.py...mmmm, open source...Modified ever so slightly

        if expanding:
            #Modify the demo.py stuff to act like pype.py:
            for line in lines:
                a = self.GetLastChild(line, -1)
                self.ShowLines(line+1,a)
                self.SetFoldExpanded(line, True)
        else:
            #Get pype.py funky(Ever so slightly modified old bean)!
            for line in lines:
                a = self.GetLastChild(line, -1)
                self.HideLines(line+1,a)
                self.SetFoldExpanded(line, False)

    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        #From demo.py (pype.py 1.1.8 uses it too!)
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)
            if level == -1:
                level = self.GetFoldLevel(line)
            if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.Expand(line, doExpand, force, visLevels-1)
                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1
        return line
        
    def IndentRegion(self) :    
        #Submitted Patch:  Franz Steinhausler
        #Submitted Patch (ModEvent Mask), Franz Steinhausler
        beg, end = self.GetSelection()
        begline = self.LineFromPosition(beg)
        endline = self.LineFromPosition(end)

        mask = self.GetModEventMask()
        self.SetModEventMask(0)

        if begline == endline:
            #This section modified by Dan
            pos = self.PositionFromLine(begline)
            self.SetSelection(pos, pos)
            self.GotoPos(pos)
            self.Tab()
            self.SetSelection(pos, self.GetLineEndPosition(begline))
            self.SetModEventMask(mask)
            return

        #Submitted Patch:  Christian Daven
        self.Tab()
        self.SetModEventMask(mask)
        
    def DedentRegion(self) :    
        #Submitted Patch:  Franz Steinhausler
        #Submitted Patch (ModEvent Mask), Franz Steinhausler
        beg, end = self.GetSelection()
        begline = self.LineFromPosition(beg)
        endline = self.LineFromPosition(end)

        mask = self.GetModEventMask()
        self.SetModEventMask(0)

        if begline == endline:
            #This section modified by Dan
            pos = self.PositionFromLine(begline)
            self.SetSelection(pos, pos)
            self.GotoPos(pos)
            self.BackTab()
            self.SetSelection(pos, self.GetLineEndPosition(begline))
            self.SetModEventMask(mask)
            return

        #Submitted Patch:  Christian Daven
        self.BackTab()
        self.SetModEventMask(mask)

    def CommentRegion(self) :    
        selstart, selend = self.GetSelection()
        #From the start of the first line selected
        oldcursorpos = self.GetCurrentPos()
        startline = self.LineFromPosition(selstart)
        self.GotoLine(startline)
        start = self.GetCurrentPos()
        #To the end of the last line selected
        #Bugfix Chris Wilson
        #Edited by Dan (selend fix)
        if selend == selstart:
            tend = selend
        else:
            tend = selend - 1
        docstring = config.prefs.doccommentstring[self.filetype]
        if os.path.splitext(self.filename)[1] == ".lua":
            docstring = "--"

        end = self.GetLineEndPosition(self.LineFromPosition(tend))
        #End Bugfix Chris Wilson
        eol = self.GetEndOfLineCharacter()
        corr = 0
        l = len(self.GetText())
        if config.prefs.doccommentmode == 0:
            self.SetSelection(start, end)
            text = docstring + self.GetSelectedText()
            text = text.replace(eol, eol + docstring)
            self.ReplaceSelection(text)
        else:
            mask = self.GetModEventMask()
            self.SetModEventMask(0)
            wpos = start
            while wpos < end:
                ws = self.GetLineIndentPosition(startline)
                le = self.GetLineEndPosition(startline)
                if ws != le:
                    self.InsertText(ws, docstring)
                startline += 1
                wpos = self.PositionFromLine(startline)
            self.SetModEventMask(mask)
        corr = len(self.GetText()) - l
        self.GotoPos(oldcursorpos + corr)

    def UnCommentRegion(self) :
        #franz: pos is not used
        selstart, selend = self.GetSelection()
        #From the start of the first line selected
        startline = self.LineFromPosition(selstart)
        oldcursorpos = self.GetCurrentPos()
        self.GotoLine(startline)
        start = self.GetCurrentPos()
        #To the end of the last line selected
        #Bugfix Chris Wilson
        #Edited by Dan (selend fix)
        if selend == selstart:
            tend = selend
        else:
            tend = selend - 1
        end = self.GetLineEndPosition(self.LineFromPosition(tend))
        #End Bugfix Chris Wilson

        mask = self.GetModEventMask()
        self.SetModEventMask(0)
        lpos = start
        newtext = ""
        l = len(self.GetText())

        docstring = config.prefs.doccommentstring[self.filetype]
        if os.path.splitext(self.filename)[1] == ".lua":
            docstring = "--"

        ldocstring = len(docstring)
        while lpos < end:
            lpos = self.PositionFromLine(startline)
            line = self.GetLine(startline)
            lc = line.find(docstring)
            if lc > -1:
                prestyle = self.GetStyleAt(lpos + lc - 1)
                style = self.GetStyleAt(lpos + lc)
                if self.filetype == 1 or os.path.splitext(self.filename)[1] == ".lua":
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
            lpos = self.PositionFromLine(startline)
        self.SetModEventMask(mask)
        self.SetSelection(start, end)
        self.ReplaceSelection(newtext.rstrip(self.GetEndOfLineCharacter()))
        corr = len(self.GetText()) - l
        self.GotoPos(oldcursorpos + corr)
   
    #**********************************************************************************
    def CenterCurrentLine(self, linenr):
        self.EnsureVisible(linenr)
        #patch: [ 1366679 ] Goto Line Should Not Display At Top Of Window
        #self.ScrollToLine(v)h
        top = linenr - self.LinesOnScreen()/2
        if top < 0:
            top = 0
        self.ScrollToLine(top)
        #self.GotoLine(linenr)
        
    def RemoveTrailingWhitespace(self):
        if not config.prefs.docremovetrailingwhitespace[self.filetype]:
                return
                
        eol = self.GetEndOfLineCharacter()
        lines = self.GetText().split(eol)
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
                curline = self.GetCurrentLine()
                self.SetText(newtext)
                #jump to saved current line
                self.GotoLine(curline)
                self.frame.SetStatusText("Removed trailing whitespaces", 2)
        if not changed:
            self.frame.SetStatusText("", 2)

    def FormatMode(self, mode) :    
        wx.BeginBusyCursor()
        wx.Yield()
        if mode == "Mac" :
            self.SetEOLMode(wx.stc.STC_EOL_CR)
            text = self.GetText()
            text = EpyGlob.FormatMacReTarget.sub('\r', text)
            self.SetText(text)
            self.OnModified(None)
        elif mode == "Unix" :
            self.SetEOLMode(wx.stc.STC_EOL_LF)
            text = self.GetText()
            text = EpyGlob.FormatUnixReTarget.sub('\n', text)
            self.SetText(text)
        elif mode == 'Win' :            
            self.SetEOLMode(wx.stc.STC_EOL_CRLF)
            text = self.GetText()
            text = EpyGlob.FormatWinReTarget.sub('\r\n', text)
            self.SetText(text)
            
        self.OnModified(None)
        wx.EndBusyCursor()
    
    def CheckSyntax(self):
        fn = self.GetFileName()
        if not self.filename:
            return False
        
        encoding = self.GetEncoding()
        ctext = drEncoding.DecodeText(self.GetText(), encoding)
        ctext = ctext.replace('\r\n', '\n').replace('\r', '\n')
        #Check Syntax First    
        try:
            compile(ctext, fn, 'exec')
        except Exception, e:
            excstr = str(e)
            result = self.RecheckSyntax.search(excstr)
            if result is not None:
                num = result.group()[5:].strip()
                try:
                    n = int(num) - 1
                    self.ScrollToLine(n)
                    self.GotoLine(n)
                    utils.ShowMessage(u'在第 %s 行处语法检查出错:\n' %num)
                    self.SetSTCFocus(True)
                    self.SetFocus()
                    #Stop the function here if something is found.
                    return False
                except:
                    utils.ShowMessage(u'语法检查出错:\n\n'+excstr, u'语法错误(Syntax Error)')
            else:
                utils.ShowMessage('语法检查出错:\n\n' + excstr, u'语法错误(Syntax Error)')

        #Now Check Indentation
        result = drTabNanny.Check(fn)
        results = result.split()
        if len(results) > 1:
            num = results[1]
            try:
                n = int(num) - 1
                self.ScrollToLine(n)
                self.GotoLine(n)
                utils.ShowMessage('tabnanny:\n' + result)
                self.SetSTCFocus(True)
                self.SetFocus()
                return False
            except:
                utils.ShowMessage('Line Number Error:\n\n'+result, 'TabNanny Trouble')

        return True
                    
    