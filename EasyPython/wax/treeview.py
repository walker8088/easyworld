# treeview.py

# todo: can we access tree like a dict?

from __future__ import generators
import wx
import waxobject
import styles
import types
import utils

class TreeView(wx.TreeCtrl, waxobject.WaxObject):

    __events__ = {
        'ItemExpanded': wx.EVT_TREE_ITEM_EXPANDED,
        'ItemExpanding': wx.EVT_TREE_ITEM_EXPANDING,
        'ItemCollapsed': wx.EVT_TREE_ITEM_COLLAPSED,
        'ItemCollapsing': wx.EVT_TREE_ITEM_COLLAPSING,
        'SelectionChanged': wx.EVT_TREE_SEL_CHANGED,
        'BeginEdit': wx.EVT_TREE_BEGIN_LABEL_EDIT,
        'EndEdit': wx.EVT_TREE_END_LABEL_EDIT,
        'ItemActivated': wx.EVT_TREE_ITEM_ACTIVATED,
        'BeginDrag': wx.EVT_TREE_BEGIN_DRAG,
        'BeginRightDrag': wx.EVT_TREE_BEGIN_RDRAG,
        'DeleteItem': wx.EVT_TREE_DELETE_ITEM,
    }

    def __init__(self, parent, size=None, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)

        wx.TreeCtrl.__init__(self, parent, wx.NewId(), size=size or (-1,-1),
         style=style)

        self.SetDefaultFont()

        self.BindEvents()
        styles.properties(self, kwargs)

    def GetChildNodes(self, node):
        """ Generator returning a node's children. <node> has to be a tree
            node, e.g. the root, or any item. """
        child, cookie = self.GetFirstChild(node)
        while child.IsOk():
            yield child
            child, cookie = self.GetNextChild(node, cookie)

    def HasChildren(self, node):
        child, cookie = self.GetFirstChild(node)
        return child.IsOk()

    def Clear(self):
        self.DeleteAllItems()
        # Clear() is used for other controls, so it makes sense to use it here
        # as well.

    def LoadFromDict(self, node, adict):
        # XXX extend this to work with objects
        items = adict.items()
        items.sort()
        for key, value in items:
            if isinstance(value, dict):
                child = self.AppendItem(node, utils.asstring(key))
                self.SetPyData(child, None) # hmm...
                self.LoadFromDict(child, value)
            else:
                child = self.AppendItem(node, utils.asstring(key))
                self.SetPyData(child, value)

    def LoadFromNestedList(self, root, list):
        """
        loads a nested list of (key, value, [children]) tuples (or lists)
        as children of the given root node. preserves the
        order of elements as they appear in the list.
        """
        for item in list:
            if (type(item) not in (types.TupleType, types.ListType)
            or len(item) not in (0, 3)):
                raise Exception, "LoadFromNestedList requires a list of (key, value, children) tuples"
            (key, value, children) = item
            node = self.AppendItem(root, utils.asstring(key))
            self.SetPyData(node, value)
            if type(children) == types.ListType:
                self.LoadFromNestedList(node, children)

    def SetImageList(self, imagelist):
        wx.TreeCtrl.SetImageList(self, imagelist)
        self._imagelist = imagelist
        # a copy must be kept around, or the images will be freed

    def SetItemImage(self, node, index, expanded=0):
        return wx.TreeCtrl.SetItemImage(self, node, index, [wx.TreeItemIcon_Normal, wx.TreeItemIcon_Expanded][expanded])

    #
    # style parameters

    _treeview_selection = {
        'single': wx.TR_SINGLE,
        'multiple': wx.TR_MULTIPLE,
        'extended': wx.TR_EXTENDED,
    }

    def _params(self, kwargs):
        flags = wx.TR_DEFAULT_STYLE
        flags |= styles.stylebool('edit_labels', wx.TR_EDIT_LABELS, kwargs)
        flags |= styles.stylebool('twist_buttons', wx.TR_TWIST_BUTTONS, kwargs)
        flags |= styles.stylebool('lines', wx.TR_NO_LINES, kwargs, reverse=1)
        flags |= styles.stylebool('hide_root', wx.TR_HIDE_ROOT, kwargs)
        flags |= styles.styledictstart('selection', self._treeview_selection, kwargs)

        # has_buttons requires special code:
        if kwargs.has_key('has_buttons'):
            if kwargs['has_buttons']:
                flags |= wx.TR_HAS_BUTTONS
            else:
                flags &= ~wx.TR_HAS_BUTTONS # make sure flag is NOT set
            del kwargs['has_buttons']
        # Note that TR_NO_BUTTONS is useless... it's 0!

        return flags
