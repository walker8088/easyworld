# grid1.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        grid = Grid(self)
        grid.EnableEditing(0)
        grid.SetGlobalSize(40, 40)
        grid[0,0] = "begin"
        grid[1,0] = "Python is dope!"

        self.AddComponent(grid, expand='both')
        self.Pack()
        self.Size = (600, 500)

app = Application(MainFrame)
app.MainLoop()
