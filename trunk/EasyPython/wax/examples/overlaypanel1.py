# overlaypanel1.py

from wax import *

WaxConfig.check_parent = True

class MainFrame(Frame):
    def Body(self):
        self.toolbar = self.MakeToolbar(self)
        self.AddComponent(self.toolbar, border=1)

        self.op = OverlayPanel(self)
        self.op.SetSize((400,300))
        self.op.SetBackgroundColour((255, 255, 0))
        self.AddComponent(self.op, expand='b')

        for s in (
            'Joho en een fles prik',
            'Blah blah...',
            'Sleeze beez',
            'This is a really long text for you',
        ):
            win = self.GenWindow(self.op, s)
            self.op.AddComponent(win, expand='b')

        self.op.Select(0)
        self.op.Pack()
        self.Pack()
        
        self.SizeY = 200

    def GenWindow(self, parent, text):
        p = Panel(parent)
        p.SetBackgroundColour((0, 0, 127))
        #p.SetSize((150, 100))   # doesn't work because of packing
        b = Button(p, text)
        p.AddComponent(b, border=20)
        p.Pack()
        return p

    def MakeToolbar(self, parent):
        p = Panel(parent, direction='h')
        for i in range(4):
            def f(event, self=self, i=i):
                self.op.Select(i)
            b = Button(p, "Select %d" % (i,), event=f)
            p.AddComponent(b)
        p.Pack()
        return p


if __name__ == "__main__":

    app = Application(MainFrame, title='test test...', direction='v')
    app.Run()

