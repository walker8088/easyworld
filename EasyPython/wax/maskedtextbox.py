# maskedtextbox.py

import wx
import wx.lib.maskededit as med
import waxobject
import sys

class MaskedTextBox(med.MaskedTextCtrl, waxobject.WaxObject):

    def __init__(self, parent, text="", *args, **kwargs):
        med.MaskedTextCtrl.__init__(self, parent, wx.NewId(), text,
         *args, **kwargs)
        print >> sys.stderr, "Don't use MaskedTextBox yet.  Names of parameters will be changed."
