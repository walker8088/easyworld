#---------------------------------------------------------------------
# findreplacedialog.py
#
#   Author: Jason Gedge
#
#   InfO:   The wax FindReplaceDialog now has pre-programmed
#           find/replace functionality to make everyone's life
#           easier. These are the functions that are required
#           to be in the control that you pass to FindReplaceDialog:
#             => GetValue;
#                   Return the string of text in the control
#             => [Get/Set]Selection;
#                   Get/set the selected text (or position of insertion)
#             => Replace;
#                   Replace a certain block of text in the control
#             => GetStringSelection;
#                   ...
#
#   TODO:
#     -
#---------------------------------------------------------------------

from messagedialog import MessageDialog
import string
import os
import wx
import waxobject

SPECIAL_ATTRS = ['GetValue', 'Replace', 'SetSelection', 'GetSelection',
                 'GetStringSelection']

class FindReplaceDialog(wx.FindReplaceDialog, waxobject.WaxObject):
    """ A Find/Replace dialog with pre-programmed find/replace functionality. """

    __events__ = {
        'Find': wx.EVT_COMMAND_FIND,
        'FindNext': wx.EVT_COMMAND_FIND_NEXT,
        'FindReplace': wx.EVT_COMMAND_FIND_REPLACE,
        'FindReplaceAll': wx.EVT_COMMAND_FIND_REPLACE_ALL,
        'FindClose': wx.EVT_COMMAND_FIND_CLOSE,
    }

    def __init__(self, parent, control=None, title="", replace=0):
        style = 0
        if replace:
            style = wx.FR_REPLACEDIALOG

        self.data = wx.FindReplaceData()
        self.data.SetFlags(wx.FR_DOWN) # search down by default
        wx.FindReplaceDialog.__init__(self, parent, self.data, title, style)

        self.parent = parent
        self.control = control
        self.nl_error_fix = False
        if isinstance(self.control, wx.TextCtrl):
            self.nl_error_fix = True
	
        for attrname in SPECIAL_ATTRS:
            setattr(self, 'f'+attrname, None)

        if control:
            for attrname in SPECIAL_ATTRS:
                f = getattr(control, attrname, None)
                setattr(self, 'f'+attrname, f)

            # Depending on what functions we got, we can handle certain events
            #   so this is where check and set the events appropriately
            if self.fGetSelection and self.fSetSelection and self.fGetValue:
                if self.fGetStringSelection and self.fReplace:
                    self.OnFindReplace = self._OnFindReplace
                    self.OnFindReplaceAll = self._OnFindReplaceAll

                self.OnFind = self._OnFind
                self.OnFindNext = self._OnFindNext

        self.BindEvents()

    #
    # This will return a tuple (start, end) specifying the start position
    #   and the end position of the string, or (-1, -1) if not found
    #
    def DoFind(self, what):
        flags = self.data.GetFlags()

        cs = 0
        if (flags & wx.FR_MATCHCASE) == wx.FR_MATCHCASE:
            cs = 1
        dir = -1
        if (flags & wx.FR_DOWN) == wx.FR_DOWN:
            dir = 1
        whole_word = 0
        if (flags & wx.FR_WHOLEWORD) == wx.FR_WHOLEWORD:
            whole_word = 1

        # Depending on direction, start/end points differ
        if dir == -1:
            start = self.fGetSelection()[0] - 1
            end = -1
        else:
            start = self.fGetSelection()[1]
            end = -2

        res = string_find( self.fGetValue(), what, start, end,
                             dir=dir, case_sensitive=cs, whole_word=whole_word,
			     nl_error_fix=self.nl_error_fix)

        return (res, res + len(what))

    #
    # The next four are the pre-programmed find/replace events
    #
    def _OnFind(self, event):
        start, end = self.DoFind(event.GetFindString())
        if start == -1:
            msg = MessageDialog(self, 'Find/Replace',
                  'Cannot find "' + event.GetFindString() + '"',
                  icon='information')
            msg.ShowModal()
        else:
            self.fSetSelection(start, end)

    def _OnFindNext(self, event):
        self._OnFind(event)

    def _OnFindReplace(self, event):
        if event.GetFindString() == '':
            return

        if self.fGetStringSelection() == event.GetFindString():
            start, end = self.fGetSelection()
            pos = start + len(event.GetReplaceString())
            self.fReplace(start, end, event.GetReplaceString())
            self.fSetSelection(pos, pos)

        self.OnFind(event)

    def _OnFindReplaceAll(self, event):
        if event.GetFindString() == '':
            return

        self.fSetSelection(0, 0)
        start, end = self.DoFind(event.GetFindString())
        while start != -1:
            pos = start + len(event.GetReplaceString())
            self.fReplace(start, end, event.GetReplaceString())
            self.fSetSelection(pos, pos)
            start, end = self.DoFind(event.GetFindString())

    #
    # The next two are kind of like a hack to prevent opening the same
    #   FindReplaceDialog twice for the one parent (which shuts down
    #   everything if it does happen)
    #
    def OnFindClose(self, event=None):
        del self.parent._fr_opened
        self.Destroy()

    def Show(self):
        try:
            tval = self.parent._fr_opened
        except AttributeError:
            self.parent._fr_opened = 5
            wx.FindReplaceDialog.Show(self)

    def ShowModal(self):
        result = self.ShowModal()
        if result == wx.ID_OK:
            return 'ok'
        else:
            return 'cancel'

#
# auxiliary functions

#
# Checks to see if the match is a whole word
#
_alphanum = string.ascii_letters + string.digits

def is_whole_word(str, what, start):
    end = start + len(what) - 1
    if (start == 0 or not str[start - 1] in _alphanum) and \
       (end == len(str) - 1 or not str[end + 1] in _alphanum):
           return True
    return False

#
# Needed because of different EOLs used by operating systems in TextBox
#
def newline_error_fix(str):
    if os.name == 'nt':		# change for overall windows
        return str.replace('\n', '\r\n')
    else:
        return str

#
# Character case checking
#
def chr_is_equal(c1, c2, case_sensitive):
    if case_sensitive:
        return c1 == c2
    else:
        return c1.lower() == c2.lower()

#
# string_find - I think the name speaks for itself
#     str: the string to search through
#    what: what you're looking for
#   start: the starting point of the search
#     end: the end point of the search
#     dir: 1 for downwards, -1 for upwards
#
#   Sloppy, but it works. I should clean this up later
#
def string_find(str, what, start, end, dir=1, case_sensitive=0, whole_word=0, nl_error_fix=1):
    """similar to string.find, except there are more options available"""

    if nl_error_fix:
        str = newline_error_fix(str)

    partial_match = False     # Set to true when a partioal match is started
    start_char = 0            # start point of 'what' string
    end_char = len(what) - 1  # end point
    # Direction is upwards, so swap start/end points
    if dir == -1:
        start_char, end_char = end_char, start_char
    curr_char = start_char    # where we are in the 'what' string
    # Yet another fix for windows. If -2 is passed, we go right to the end
    if end == -2:
        end = len(str)
    # An iterator to go over the search string
    xiter = xrange(start, end, dir).__iter__()
    y = 0
    # If case sensitive, lowercase everything
    if case_sensitive == 0:
        what = what.lower()

    try:
        # StopIteration exception should break this loop
        while True:
            # Get the next position in the search string
            x = xiter.next()
            # Get current character (lowercase if case sensitive)
            char_check = str[x]
            # If that char is same as the char were looking at
            if chr_is_equal(char_check, what[curr_char], case_sensitive):
                # If we're at the end of the 'what' string
                if curr_char == end_char:
                    # One must also include the # of newlines :/
                    pos = x - curr_char
                    # Check for whole word match if required
                    if whole_word == 1:
                        if is_whole_word(str, what, pos):
                            return pos# + newline_error_fix(str, x)
                        else: # not a whole word, start again
                            curr_char = start_char
                            if partial_match and chr_is_equal(char_check, what[curr_char], case_sensitive):
                                xiter = xrange(x, end, dir).__iter__()
                    else:
                        return pos# + newline_error_fix(str, x)
                else:
                    # Not at the end, go to the next character
                    curr_char += dir
                    partial_match = True
            else:
                # Not the same char, let's revert back
                curr_char = start_char
                if partial_match and chr_is_equal(char_check, what[curr_char], case_sensitive):
                    xiter = xrange(x, end, dir).__iter__()
    except StopIteration:
        pass
    # Never found it
    return -1

