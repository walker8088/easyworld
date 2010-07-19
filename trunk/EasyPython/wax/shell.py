# shell.py

import wx
from wx.py import shell, version, filling

import waxobject
from splitter import Splitter

class PyCrust(shell.Shell, waxobject.WaxObject):

    def __init__(self, parent):
        id = wx.NewId()
        intro = "Welcome to PyCrust %s - The Flakiest Python Shell" % (
                version.VERSION)
        shell.Shell.__init__(self, parent, id, introText=intro)
        self.id = id

class PyCrustFilling(Splitter):

    def __init__(self, parent, fillerwinsize=150):
        id_shell = wx.NewId()
        id_filling = wx.NewId()
        intro = "Welcome to PyCrust %s - The Flakiest Python Shell" % (
                version.VERSION)
        Splitter.__init__(self, parent, size=(640,480))
        shellwin = PyCrust(self)
        fillingwin = filling.Filling(self, id_filling, size=(640,480),
                     rootObject=shellwin.interp.locals, rootIsNamespace=1)
        self.Split(shellwin, fillingwin, direction='horizontal')
        px, py = parent.GetSize()
        if py - fillerwinsize > 0:
            self.SetSashPosition(py - fillerwinsize)

        # keep references around
        self.shellwin = shellwin
        self.fillingwin = fillingwin
