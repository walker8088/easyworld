# styledtextbox.py

# todo: component styles (like e.g. TextBox), if possible
# XXX Lots of work to be done on this one...

import wx
import wx.stc as stc
import waxobject

# create a method that calls StyledTextBox.SendMsg with a given code
def _bindcmd(code):
    def cmd(self):
        self.SendMsg(code)
    return cmd

class StyledTextBox(waxobject.WaxObject, stc.StyledTextCtrl):

    __events__ = {
        'Char': wx.EVT_CHAR,
        'CharAdded': stc.EVT_STC_CHARADDED, # a character was added
        'Change': stc.EVT_STC_CHANGE,
         # change is made to the text of the document, except for styles
        'DoubleClick': stc.EVT_STC_DOUBLECLICK,
        'MarginClick': stc.EVT_STC_MARGINCLICK,
        'Modified': stc.EVT_STC_MODIFIED,
         # document was modified, including style changes
        'Paint': stc.EVT_STC_PAINTED, # occurs after all painting is complete
        #'PosChanged': stc.EVT_STC_POSCHANGED,  # deprecated
        'StyleNeeded': stc.EVT_STC_STYLENEEDED,
        'UpdateUI': stc.EVT_STC_UPDATEUI,
    }

    def __init__(self, parent, size=(125,-1)):
        # TODO: set lots of options here

        style = 0
        stc.StyledTextCtrl.__init__(self, parent, wx.NewId(), size=size,
         style=style)
        self._language = None

        self.BindEvents()
	
    #
    # events

    # this dummy method is necessary, otherwise the StyledTextBox starts
    # complaining... probably because the existing OnPaint method will be
    # hooked up to stc.EVT_STC_PAINTED, which is Wrong.
    def OnPaint(self, event):
        event.Skip()

    def write(self, s):
        # Added so we can use a TextBox as a file-like object and redirect
        # stdout to it.
        self.AddText(s)

    #
    # synchronize part of the APIs of TextBox and StyledTextBox

    def AppendText(self, s):
        self.AddText(s)

    def Clear(self):
        self.ClearAll()

    def GetValue(self):
        return self.GetText()

    def GetStringSelection(self):
        return self.GetSelectedText()

    def Replace(self, start, end, text):
        self.SetTargetStart(start)
	self.SetTargetEnd(end)
	self.ReplaceTarget(text)

    def GetCurrentLineNumber(self):
        return self.LineFromPosition(self.GetCurrentPos())

    def GetLineText(self, lineno):
        return self.GetLine(lineno)

    #
    # cursor

    CursorEnd = _bindcmd(stc.STC_CMD_LINEEND)
    CursorHome = _bindcmd(stc.STC_CMD_HOME)
    CursorRight = _bindcmd(stc.STC_CMD_CHARRIGHT)
    CursorLeft = _bindcmd(stc.STC_CMD_CHARLEFT)
    CursorDocumentStart = _bindcmd(stc.STC_CMD_DOCUMENTSTART)
    CursorDocumentEnd = _bindcmd(stc.STC_CMD_DOCUMENTEND)

    #
    # editing

    DeleteCurrentLine = _bindcmd(stc.STC_CMD_LINEDELETE)

    #
    # line endings

    def GetEOLMode(self):
        """ Return the EOL mode.  This is a string that can be 'mac', 'dos',
            or 'unix'. """
        eolmode = stc.StyledTextCtrl.GetEOLMode(self)
        return _eol_to_string[eolmode]

    def SetEOLMode(self, mode):
        """ Set the EOL mode.  <mode> can be a STC flag, or a string 'unix',
            'dos', 'windows' or 'mac'.  ('dos' and 'windows' are the same.) """
        if isinstance(mode, basestring):
            mode = _string_to_eol[mode]
        stc.StyledTextCtrl.SetEOLMode(self, mode)

    def ConvertEOLs(self, mode):
        """ Convert the line endings to the given mode.  <mode> can be a STC
            flag, or a string 'unix', 'dos', 'windows', or 'mac'. """
        if isinstance(mode, basestring):
            mode = _string_to_eol[mode]
        stc.StyledTextCtrl.ConvertEOLs(self, mode)

    #
    # styles

    def _getstyleconst(self, name):
        try:
            return language_states[self._language][name]
        except KeyError:
            pass

        try:
            return other_styles[name]
        except KeyError:
            raise KeyError, "Unknown style name '%s'" % (name,)

    def SetLanguage(self, language):
        self._language = language
        langconst = languages[language]
        self.SetLexer(langconst)

    def SetStyle(self, state, style):
        #stateconst = language_states[self._language][state]
        const = self._getstyleconst(state)
        self.StyleSetSpec(const, style)

    def StyleSetFont(self, style, font):
        """ If self._language is set, this can be called with a string for
            <state>, e.g. 'default' or 'comment', etc. """
        if isinstance(style, str) or isinstance(style, unicode):
            #style = language_states[self._language][style]
            style = self._getstyleconst(style)
        stc.StyledTextCtrl.StyleSetFont(self, style, font)

    def SetFont(self, font):
        if self._language and self._language != 'container':
            for name, value in language_states[self._language].items():
                self.StyleSetFont(value, font)
        else:
            self.StyleSetFont(stc.STC_STYLE_DEFAULT, font)

#
# styles

# XXX maybe a wrapper function can be used to make the style strings

# languages supported by the STC lexer
languages = {
    'container': stc.STC_LEX_CONTAINER,
    'null': stc.STC_LEX_NULL,
    'python': stc.STC_LEX_PYTHON,
    'c++': stc.STC_LEX_CPP,
    'html': stc.STC_LEX_HTML,
    'xml': stc.STC_LEX_XML,
    'lisp': stc.STC_LEX_LISP,
    'scheme': stc.STC_LEX_LISP,
    'ruby': stc.STC_LEX_RUBY,
    'groovy': stc.STC_LEX_RUBY,   # for now, this will have to do
    # XXX more...
}

language_states = {
    'python': {
        'default': stc.STC_P_DEFAULT,
        'comment': stc.STC_P_COMMENTLINE,
        'number': stc.STC_P_NUMBER,
        'string': stc.STC_P_STRING,
        'character': stc.STC_P_CHARACTER,
        'keyword': stc.STC_P_WORD,
        'triple_string': stc.STC_P_TRIPLE,
        'triple_double_string': stc.STC_P_TRIPLEDOUBLE,
        'classname': stc.STC_P_CLASSNAME,
        'defname': stc.STC_P_DEFNAME,
        'operator': stc.STC_P_OPERATOR,
        'identifier': stc.STC_P_IDENTIFIER,
        'comment_block': stc.STC_P_COMMENTBLOCK,
        'string_eol': stc.STC_P_STRINGEOL,
    },

    'lisp': {
        'default': stc.STC_LISP_DEFAULT,
        'comment': stc.STC_LISP_COMMENT,
        'number': stc.STC_LISP_NUMBER,
        'keyword': stc.STC_LISP_KEYWORD,
        'string': stc.STC_LISP_STRING,
        'stringeol': stc.STC_LISP_STRINGEOL,
        'identifier': stc.STC_LISP_IDENTIFIER,
        'operator': stc.STC_LISP_OPERATOR,
    },

    'groovy': {
    },

    # XXX add more languages
}
language_states['scheme'] = language_states['lisp']

other_styles = {
    'line_number': stc.STC_STYLE_LINENUMBER,
    'brace_bad': stc.STC_STYLE_BRACEBAD,
    'brace_match': stc.STC_STYLE_BRACELIGHT,
    'default': stc.STC_STYLE_DEFAULT,
}

_eol_to_string = {
    stc.STC_EOL_CR: 'mac',      # \r
    stc.STC_EOL_CRLF: 'dos',    # \r\n
    stc.STC_EOL_LF: 'unix'      # \n
}

_string_to_eol = {
    'unix': stc.STC_EOL_LF,
    'dos': stc.STC_EOL_CRLF,
    'windows': stc.STC_EOL_CRLF,
    'mac': stc.STC_EOL_CR,
}
