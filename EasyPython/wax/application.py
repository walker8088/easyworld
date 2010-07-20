# application.py

import wx
import sys
from waxconfig import WaxConfig
import font
import traceback

class Application(wx.App):
    def __init__(self, frameklass, *args, **kwargs):
        # takes a frame *class* plus arbitrary options.  these options will
        # be passed to the frame constructor.
        self.frameklass = frameklass
        self.args = args
        self.kwargs = kwargs

        # when set, the app uses the stdout/stderr window; off by default
        use_stdout_window = 0
        if kwargs.has_key('use_stdout_window'):
            use_stdout_window = kwargs['use_stdout_window']
            del kwargs['use_stdout_window']
        wx.App.__init__(self, use_stdout_window)

    def OnInit(self):
        if isinstance(WaxConfig.default_font, tuple):
            WaxConfig.default_font = font.Font(*WaxConfig.default_font)
        else:
            print >> sys.stderr, "Warning: This construct will not work in future wxPython versions"
        self.mainframe = self.frameklass(*self.args, **self.kwargs)
        
        if hasattr(self.mainframe.__class__, "__ExceptHook__"):
            sys.excepthook = self.mainframe.__ExceptHook__
        else :
            sys.excepthook = self.__ExceptHook__
        
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        
        self.mainframe.Show(True)
        self.SetTopWindow(self.mainframe)
        return True
    
    def OnActivate(self, event):
        if event.GetActive():
            self.mainframe.OnActivate()
        event.Skip()
    
    def Run(self):
        self.MainLoop()
        self.Unbind(wx.EVT_ACTIVATE_APP) # needed for wxpython 2.9, else deadobject error, because of delivering event
    
    def __ExceptHook__(self, exctype, value, tb):
        s = ''.join(traceback.format_exception(exctype, value, tb))
        dlg = wx.lib.dialogs.ScrolledMessageDialog(None, s, "ErrorInfo")
        dlg.ShowModal()
        dlg.Destroy()
    
# TODO:
# it should be easy to set font, icon, etc...
