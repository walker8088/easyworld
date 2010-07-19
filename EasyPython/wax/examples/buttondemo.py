# buttondemo.py
# Demonstrate buttons and boxsizers.
# 2003.05.18: Rewritten to work with the new Application format.

import sys
sys.path.append("../..")

from wax import *

# stick a custom event in Button
def MyOnClick(self, event):
    print 'U clicked the button with label', `self.GetLabel()`
Button.OnClick = MyOnClick

class MainFrame(Frame):

    def Body(self):
        self.AddComponent(Button(self, "one"), stretch=1)
        self.AddComponent(Button(self, "two"), expand=1, stretch=1)
        self.AddComponent(Button(self, "three"), stretch=1)

        # adding a panel, using a class
        class Panel1(Panel):
            def Body(self):
                self.AddComponent(Button(self, "AAA"), stretch=1)
                self.AddComponent(Button(self, "BBB"), expand=1, stretch=1)
                self.AddComponent(Button(self, "CCC"), stretch=1)

        panel1 = Panel1(self, direction="HORIZONTAL")
        panel1.Pack()
        self.AddComponent(panel1, stretch=1)

        # adding two nested panels
        panel2 = Panel(self, direction="H")
        panel2.AddComponent(Button(panel2, "DD"), expand=1, stretch=1)
        panel2.AddComponent(Button(panel2, "EE"), expand=1, stretch=1)

        panel3 = Panel(panel2, direction="V")
        panel3.AddComponent(Button(panel3, "999"), stretch=1)
        b = Button(panel3, "888")
        panel3.AddComponent(b, expand=1, stretch=1)
        panel3.Pack()
        panel2.AddComponent(panel3, stretch=1)

        panel2.Pack()
        self.AddComponent(panel2, expand=1, stretch=1)

        self.Pack()

        # override event for this button
        def my_event(event):
            print "Wahey!"
        b.OnClick = my_event

app = Application(MainFrame, direction='vertical', title="Test test...")
app.MainLoop()
