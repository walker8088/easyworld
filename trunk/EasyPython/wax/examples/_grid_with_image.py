# grid_with_image.py
# DOES NOT WORK in wxPython 2.6 (and maybe 2.5) because the SetCellBitmap
# method seems to be missing.

from wax import *

class MainFrame(Frame):
    def Body(self):
        grid = Grid(self)
        grid.EnableEditing(0)
        grid.SetGlobalSize(40, 40)

        icon = Image("heretic2.ico")
        data = icon.ConvertToBitmap()
        grid.SetCellBitmap(data, 2, 2)
        # apparently this isn't possible anymore >=(

app = Application(MainFrame)
app.MainLoop()
