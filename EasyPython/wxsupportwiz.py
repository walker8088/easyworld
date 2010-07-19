#!/usr/bin/env python
"""
wxPython Technical Support Wizard (sort of).

Usage: wxsupportwiz.wxAddExceptHook('http://host.com/error.php')

- what happens if this is run when unconnected to the net?
- would be nice if the user could optionally enter some information about the problem, though of course I don't want it to get so complex that the user just cancels it

This sends the data using a CGI instead of by email because there's no guarantee that the user has setup an email account with MAPI.
Or I could always just bring up the user's web browser to a form already partially filled out.
The CGI could automatically match the error data to answers to already solved problems and suggest those.
So the whole wizard should probably be on the web.
For FAQs, could record how popular each answer is and then shown links to the top N answers.

can see XatXesizerDoc.cpp for a MAPI example. useful only for automatically including the user's email address
x automatically getting the user's email address seems hard, and what if there are multiple accounts, or none?

- sending the program's log would be nice to send too

The more work you postpone in your wxPython app until the wxWindows event loop has started, the more errors this will be able to catch.

If the cgi prints a line, this will assume it's a url and try to point the user's web browser to it. So you could, eg, popup help on the problem.

Having an exception occur in your exception handler is annoying.
"""

__author__ = 'Patrick Roberts'
__copyright__ = 'Copyright 2004 Patrick Roberts'
__license__ = 'Python'
__version__ = '1.0'

import os, platform, urllib, sys, time, traceback, urlparse, webbrowser
import wx


def get_last_traceback(tb):
    while tb.tb_next:
        tb = tb.tb_next
    return tb


def format_namespace(d, indent=''):#    '):
    return '\n'.join(['%s%s: %s' % (indent, k, repr(v)[:10000]) for k, v in d.iteritems()])


ignored_exceptions = [] # a problem with a line in a module is only reported once per session

def wxAddExceptHook(cgi_url, app_version='[No version]'):#, ignored_exceptions=[]):
    """
    wxMessageBox can't be called until the app's started
    - It would be nice if this used win32 directly, and didn't depend on wx being started, cuz that can't handle initial errors. Maybe have a temporary initial error handler that just uses a standard windows message dlg, then switch once wx is going.
    """
    
    def handle_exception(e_type, e_value, e_traceback):
        traceback.print_exception(e_type, e_value, e_traceback) # this is very helpful when there's an exception in the rest of this func
        last_tb = get_last_traceback(e_traceback)
        ex = (last_tb.tb_frame.f_code.co_filename, last_tb.tb_frame.f_lineno)
        if ex not in ignored_exceptions:
            ignored_exceptions.append(ex)
            ##message = "An uncaught error occurred.\n\nDo you mind if an error report is sent to %s?"
            #message = "Do you mind if an error report is sent to %s?"
            #message
            #if wx.MessageBox(message % urlparse.urlparse(cgi_url)[1], 'Uncaught Error', wx.OK|wx.CANCEL|wx.ICON_ERROR) == wx.OK:
            #print 'woof', `wx.GetTextFromUser('x')` # badly returns '' on cancel
            dlg = wx.TextEntryDialog(None, "Do you mind if an error report is sent to %s?\n\nIf you want to be contacted when a solution is found, please enter your e-mail address:" % urlparse.urlparse(cgi_url)[1], 'Uncaught Error', '', wx.OK|wx.CANCEL) #|wx.ICON_ERROR) -- can use that style only with wx.MessageBox
            result = dlg.ShowModal()
            email_addr = dlg.GetValue()
            dlg.Destroy()
            if result == wx.ID_OK:
                info = {
                    'app-title' : wx.GetApp().GetAppName(), # app_title
                    'app-version' : app_version,
                    'wx-version' : wx.VERSION_STRING,
                    'wx-platform' : wx.Platform,
                    'python-version' : platform.python_version(), #sys.version.split()[0],
                    'platform' : platform.platform(),
                    'e-type' : e_type,
                    'e-value' : e_value,
                    'date' : time.ctime(),
                    'cwd' : os.getcwd(),
                    'e-mail' : email_addr, # have to be careful about this colliding with some error.php variable; using a dash probably suffices
                    }
                if e_traceback:
                    info['traceback'] = ''.join(traceback.format_tb(e_traceback)) + '%s: %s' % (e_type, e_value)
                    last_tb = get_last_traceback(e_traceback)
                    exception_locals = last_tb.tb_frame.f_locals # the locals at the level of the stack trace where the exception actually occurred
                    info['locals'] = format_namespace(exception_locals)
                    if 'self' in exception_locals:
                        info['self'] = format_namespace(exception_locals['self'].__dict__)
                if sys.platform == 'win32':
                    import win32api
                    info['user-name'] = win32api.GetUserName()

                busy = wx.BusyCursor()
                try:
                    f = urllib.urlopen(cgi_url, data=urllib.urlencode(info))
                except IOError:
                    pass
                else:
                    #url = f.get_url()
                    #if url != cgi_url:
                    url = f.readline().strip()
                    if url:
                        webbrowser.open_new(url)
                del busy


    sys.excepthook = lambda *args: wx.CallAfter(handle_exception, *args) # this callafter may be unnecessary since it looks like threads ignore sys.excepthook; could have all a thread's code be contained in a big try clause (possibly by subclassing Thread and replacing run())
