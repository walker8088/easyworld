# listview.py

import wx
import waxobject
import styles
import colordb
import utils

# todo: mixins

class ListItemAttr(wx.ListItemAttr):
    def SetBackgroundColor(self, x):
        return self.SetBackgroundColour(x)
    # fixme: more color methods

class ListView(wx.ListCtrl, waxobject.WaxObject):

    __events__ = {
        'BeginDrag': wx.EVT_LIST_BEGIN_DRAG,
        'BeginRightDrag': wx.EVT_LIST_BEGIN_RDRAG,
        'BeginLabelEdit': wx.EVT_LIST_BEGIN_LABEL_EDIT,
        'DeleteItem': wx.EVT_LIST_DELETE_ITEM,
        'DeleteAllItems': wx.EVT_LIST_DELETE_ALL_ITEMS,
        'EndLabelEdit': wx.EVT_LIST_END_LABEL_EDIT,
        'ItemSelected': wx.EVT_LIST_ITEM_SELECTED,
        'ItemDeselected': wx.EVT_LIST_ITEM_DESELECTED,
        'ItemDoubleClick': wx.EVT_LIST_ITEM_ACTIVATED,
        'ItemActivated': wx.EVT_LIST_ITEM_ACTIVATED,    # use one or the other
        'ItemFocused': wx.EVT_LIST_ITEM_FOCUSED,
        'ItemMiddleClick': wx.EVT_LIST_ITEM_MIDDLE_CLICK,
        'ItemRightClick': wx.EVT_LIST_ITEM_RIGHT_CLICK,
        'InsertItem': wx.EVT_LIST_INSERT_ITEM,
        'KeyDown': wx.EVT_LIST_KEY_DOWN,
        'ColumnClick': wx.EVT_LIST_COL_CLICK,
        'ColumnRightClick': wx.EVT_LIST_COL_RIGHT_CLICK,
        'ColumnBeginDrag': wx.EVT_LIST_COL_BEGIN_DRAG,
        'ColumnDragging': wx.EVT_LIST_COL_DRAGGING,
        'ColumnEndDrag': wx.EVT_LIST_COL_END_DRAG,
        'CacheHint': wx.EVT_LIST_CACHE_HINT,
    }

    def __init__(self, parent, size=None, columns=(), **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)

        wx.ListCtrl.__init__(self, parent, wx.NewId(), size=size or (-1,-1),
         style=style)

        # easy column insertion
        if columns:
            for i in range(len(columns)):
                self.InsertColumn(i, columns[i])

        self.BindEvents()

        self.SetDefaultFont()
        styles.properties(self, kwargs)

    def SetColumnWidths(self, widths):
        """ Set the widths of all columns.  A value of -1 means no change. """
        for index in range(len(widths)):
            width = widths[index]
            if width != -1:
                self.SetColumnWidth(index, width)

    def InsertColumn(self, column, name, *args, **kwargs):
        wx.ListCtrl.InsertColumn(self, column, name, *args, **kwargs)
        # XXX do some nice things here for image columns

    def InsertRow(self, row, *args):
        self.InsertStringItem(row, '')
        for i in range(len(args)):
            self.SetStringItem(row, i, utils.asstring(args[i]))
        self.SetItemData(row, row)
        return row

    def AppendRow(self, *args):
        numrows = self.GetItemCount()
        self.InsertRow(numrows, *args)
        return numrows  # index of item being inserted

    def __setitem__(self, index, value):
        assert isinstance(index, tuple) and len(index) == 2
        row, column = index
        self.ExpandTo(row+1)    # make sure we have enough rows
        self.SetStringItem(row, column, utils.asstring(value))

    def __getitem__(self, index):
        assert isinstance(index, tuple) and len(index) == 2
        row, column = index
        return self.GetStringItem(row, column)

    def GetStringItem(self, row, column):
        # there is a SetStringItem, so why not a GetStringItem, eh?  Especially
        # since there doesn't seem to be an easy way to retrieve the value
        # of a "cell"...
        listitem = self.GetItem(row, column)
        return listitem.GetText()

    def ExpandTo(self, numrows):
        """ Expand the ListView so it has at least <numrows> rows. """
        base = self.GetItemCount()
        diff = numrows - base
        if diff > 0:
            for i in range(diff):
                self.InsertRow(i + base)

    def GetSelected(self):
        """ Return a list of (indexes of) selected items. """
        items = []
        item = self.GetFirstSelected()
        while item > -1:
            items.append(item)
            item = self.GetNextSelected(item)
        return items

    def SetImageList(self, imagelist, small=1):
        wx.ListCtrl.SetImageList(self, imagelist, [wx.IMAGE_LIST_NORMAL, wx.IMAGE_LIST_SMALL][small])
        self._imagelist = imagelist

    #
    # alternate color methods

    def GetItemBackgroundColor(self, idx):
        return wx.ListCtrl.GetItemBackgroundColour(self, idx)

    def SetItemBackgroundColor(self, idx, color):
        color = colordb.convert_color(color)
        wx.ListCtrl.SetItemBackgroundColour(self, idx, color)

    def GetItemTextColor(self, idx):
        return wx.ListCtrl.GetItemTextColour(self, idx)

    def SetItemTextColor(self, idx, color):
        color = colordb.convert_color(color)
        wx.ListCtrl.SetItemTextColour(self, idx, color)

    #
    # style parameters

    _listview_rules = {
        'horizontal': wx.LC_HRULES,
        'vertical': wx.LC_VRULES,
        'both': wx.LC_HRULES | wx.LC_VRULES,
    }

    _listview_icons = {
        'large': wx.LC_ICON,
        'small': wx.LC_SMALL_ICON,
    }

    _listview_icon_alignment = {
        'top': wx.LC_ALIGN_TOP,
        'left': wx.LC_ALIGN_LEFT,
    }

    _listview_sort = {
        'ascending': wx.LC_SORT_ASCENDING,
        'descending': wx.LC_SORT_DESCENDING,
    }

    def _params(self, kwargs):
        flags = 0
        flags |= styles.stylebooleither('report', wx.LC_REPORT, wx.LC_LIST, kwargs)
        if not ((flags & wx.LC_REPORT) or (flags & wx.LC_LIST)):
            flags |= wx.LC_REPORT
        flags |= styles.stylebool('virtual', wx.LC_VIRTUAL, kwargs)
        flags |= styles.stylebool('single_selection', wx.LC_SINGLE_SEL, kwargs)
        flags |= styles.styledictstart('rules', self._listview_rules, kwargs)
        flags |= styles.styledictstart('icons', self._listview_icons, kwargs)
        flags |= styles.styledictstart('icon_alignment', self._listview_icon_alignment, kwargs)
        flags |= styles.stylebool('icon_autoarrange', wx.LC_AUTOARRANGE, kwargs)
        flags |= styles.stylebool('edit_labels', wx.LC_EDIT_LABELS, kwargs)
        flags |= styles.stylebool('noheader', wx.LC_NO_HEADER, kwargs)
        flags |= styles.styledictstart('sort', self._listview_sort, kwargs)

        return flags
