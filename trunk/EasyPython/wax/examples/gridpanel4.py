# flexgridpanel1.py

from wax import *

class MainFrame(Frame):

    def Body(self):
        def b(text):
            import wx
            b = Button(p, text, size=bsize)
            b.SetPosition(wx.DefaultPosition)
            return b
        bsize = (100, 50)
        p = GridPanel(self, rows=3, cols=3, hgap=3, vgap=3)
        p.SetBackgroundColour((0, 0, 0xFF))
        p.AddComponent(0, 0, b('one'), align='tl', expand=0)
        p.AddComponent(1, 0, b('two'), align='th', expand=0)
        p.AddComponent(2, 0, b('three'), expand=0, align='tr')
        p.AddComponent(0, 1, b('four'), expand=0, align='vl')
        p.AddComponent(1, 1, b('five'), expand=0, align='c')
        p.AddComponent(2, 1, b('six'), expand=0, align='vr')
        p.AddComponent(0, 2, b('seven'), expand=0, align='bl')
        p.AddComponent(1, 2, b('eight'), expand=0, align='bh')
        p.AddComponent(2, 2, b('nine'), expand=0, align='br')
        # Note that the expand=0 is important, otherwise the alignment won't
        # work (because the control will just fill up the available space
        # rather than align to it)
        p.Pack()
        self.AddComponent(p, expand='both')
        self.Pack()

if __name__ == "__main__":

    app = Application(MainFrame, title='GridPanel demo', direction='v')
    app.Run()

