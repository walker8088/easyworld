# grid.py

# todo: styles

import wx
import wx.grid as gridlib
import waxobject
import waxconfig

class Grid(gridlib.Grid, waxobject.WaxObject):

    def __init__(self, parent, numrows=10, numcolumns=10):
        gridlib.Grid.__init__(self, parent, wx.NewId())
        self.SetDefaultFont()
        self.CreateGrid(numrows, numcolumns)

    def SetDefaultFont(self):
        font = waxconfig.WaxConfig.default_font
        self.SetDefaultCellFont(font)

    def SetGlobalSize(self, rowsize, colsize):
        """ Set all cells to the same size. """
        for i in range(self.GetNumberRows()):
            self.SetRowSize(i, rowsize)
        for i in range(self.GetNumberCols()):
            self.SetColSize(i, colsize)

    def __setitem__(self, index, value):
        assert isinstance(index, tuple) and len(index) == 2
        row, column = index
        self.SetCellValue(row, column, value)

    def __getitem__(self, index):
        assert isinstance(index, tuple) and len(index) == 2
        row, column = index
        return self.GetCellValue(row, column)

