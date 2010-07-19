# properties-1.py
# Demonstrates pseudo-properties.  E.g. print obj.Size is a shorthand for
# print obj.GetSize(), and obj.Size = (x, y) is a shorthand for
# obj.SetSize((x, y)).

from wax import *

class MainFrame(Frame):
    def Body(self):
        p = Panel(self)
        self.AddComponent(p, expand=1, stretch=1)

        print "Frame size/position:", self.Size, self.Position
        print "Panel size/position:", p.Size, p.Position
        p.BackgroundColor = 'red'

        # normal attributes still work
        self.foobar = 42
        print self.foobar

app = Application(MainFrame)
app.Run()
