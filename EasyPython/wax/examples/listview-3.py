# listview-3.py
# By Stefan Rank.  Minor modifications by Hans Nowak.
# Requires Wax 0.3.13 or better.

import wax
import wx


class AutoWidthListView(wax.ListView):
    """inspired by wx.lib.mixins.AutoWidthListCtrlMixin. Automatically resizes 
       columns in the ListView to take up all available space. It does not use 
       the last column but equally divides it between columns.
    """

    def OnResize(self, event):
        wax.core.CallAfter(self._doResize)
        event.Skip()

    def OnColumnBeginDrag(self, event):
        if event.GetColumn() == self.ColumnCount - 1:
            event.Veto() # only inner column-separators can be dragged
        else:
            event.Skip()

    def OnColumnEndDrag(self, event):
        wax.core.CallAfter(self._doResize, fixedcolumn=event.GetColumn())
        event.Skip()

    def _doResize(self, fixedcolumn=None):
        """We expand or contract all columns to take up the remaining free space."""
        if not self: # avoid a PyDeadObject error
            return
        numCols = self.ColumnCount
        if numCols <= 0:
            return # Nothing to resize.
        # We're showing the vertical scrollbar -> allow for scrollbar width
        # NOTE: on GTK, the scrollbar is included in the client size, but on Windows it's not
        listWidth = self.GetClientSize().width
        if wax.core.Platform != '__WXMSW__':
            if self.GetItemCount() > self.GetCountPerPage():
                scrollWidth = wax.SystemSettings.GetMetric('vscroll_x')
                listWidth = listWidth - scrollWidth
        totColWidth = sum([self.GetColumnWidth(col) for col in range(numCols)])
        widthdiff = listWidth - totColWidth - 1
        if fixedcolumn is None:
            # expand/contract columns equally
            newwidths = [self.GetColumnWidth(col) + widthdiff // numCols
                         for col in range(numCols)]
        else:
            newwidths = [self.GetColumnWidth(col) for col in range(numCols)]
            colstochange = numCols - (fixedcolumn + 1)
            for index in range(fixedcolumn + 1, numCols):
                newwidths[index] += (widthdiff // colstochange)
        self.SetColumnWidths(newwidths)


if __name__ == "__main__":

    app = wax.Application(wax.Frame)
    app.mainframe.AddComponent(AutoWidthListView(app.mainframe, columns=('A','B')), expand='both')
    app.mainframe.Pack()
    app.mainframe.Size = 200, 200
    app.Run()
    