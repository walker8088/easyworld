# waxobject-get-all-children-1.py

from wax import *

class MainFrame(VerticalFrame):
    def Body(self):
        p = Panel(self)
        b = Button(p, "And another one...", event=self.OnClickButton)
        p.AddComponent(b, border=5)
        p.Pack()
        self.AddComponent(p, expand='h')

        p2 = self.MakePanel2(self)
        self.AddComponent(p2, expand='both')

        self.Pack()

        # create the generator
        self.g = self.GetAllChildren()
        p.BackgroundColor = 'red'

    def MakePanel2(self, parent):
        p = Panel(parent, direction='v')
        p.AddComponent(Button(p, "one"), expand='h')
        p.AddComponent(Button(p, "two"), expand='both')
        p.AddComponent(Button(p, "three"), expand='h')

        # adding a panel, using a class
        class Panel1(Panel):
            def Body(self):
                self.AddComponent(Button(self, "AAA"))
                self.AddComponent(Button(self, "BBB"), expand='h')
                self.AddComponent(Button(self, "CCC"))

        panel1 = Panel1(p, direction="HORIZONTAL")
        panel1.Pack()
        p.AddComponent(panel1, expand='h')

        # adding two nested panels
        panel2 = Panel(p, direction="H")
        panel2.AddComponent(Button(panel2, "DD"), expand='b')
        panel2.AddComponent(Button(panel2, "EE"), expand='b')

        panel3 = Panel(panel2, direction="V")
        panel3.AddComponent(Button(panel3, "999"))
        b = Button(panel3, "888")
        panel3.AddComponent(b, expand='both')
        panel3.Pack()
        panel2.AddComponent(panel3, expand='vertical')

        panel2.Pack()
        p.AddComponent(panel2, expand='b', border=5)

        p.Pack()
        return p

    def OnClickButton(self, event):
        try:
            obj = self.g.next()
        except StopIteration:
            ShowMessage("Done", "No more children left")
        else:
            print "Coloring:", obj
            obj.BackgroundColor = 'yellow'
            obj.Refresh() # in some cases, this is necessary to show the color

app = Application(MainFrame)
app.Run()
