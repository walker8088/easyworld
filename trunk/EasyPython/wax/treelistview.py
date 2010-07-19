# treelistview.py

import styles
import wx
import wx.gizmos as gizmos
import waxobject
import treeview

class TreeListView(gizmos.TreeListCtrl, waxobject.WaxObject):

    def __init__(self, parent, columns=(), size=None, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
        gizmos.TreeListCtrl.__init__(self, parent, wx.NewId(),
         size=size or (-1,-1), style=style)

        for name in columns:
            self.AddColumn(name)

        self.SetDefaultFont()
        self.BindEvents()
        styles.properties(self, kwargs)

    # some deviltry to copy styles stuff from TreeView...
    _treeview_selection = treeview.TreeView._treeview_selection
    _params = treeview.TreeView._params.im_func
    # I'll come up with a better solution later.

