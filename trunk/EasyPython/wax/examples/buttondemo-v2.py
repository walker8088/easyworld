# buttondemo-v2.py
# Demonstrate buttons and boxsizers.
# 2003.05.18: Rewritten to work with the new Application format.
# 2004.07.22: Now uses new expand parameters.

import sys
sys.path.append("../..")

from wax import *

# stick a custom event in Button
def MyOnClick(self, event):
    print 'U clicked the button with label', `self.GetLabel()`
Button.OnClick = MyOnClick

class MainFrame(Frame):

    def Body(self):
        self.AddComponent(Button(self, "one"), expand='h')
        self.AddComponent(Button(self, "two"), expand='both')
        self.AddComponent(Button(self, "three"), expand='h')

        # adding a panel, using a class
        class Panel1(Panel):
            def Body(self):
                self.AddComponent(Button(self, "AAA"))
                self.AddComponent(Button(self, "BBB"), expand='h')
                self.AddComponent(Button(self, "CCC"))

        panel1 = Panel1(self, direction="HORIZONTAL")
        panel1.Pack()
        self.AddComponent(panel1, expand='h')

        # adding two nested panels
        panel2 = Panel(self, direction="H")
        panel2.AddComponent(Button(panel2, "DD"), expand='b')
        panel2.AddComponent(Button(panel2, "EE"), expand='b')

        panel3 = Panel(panel2, direction="V")
        panel3.AddComponent(Button(panel3, "999"))
        b = Button(panel3, "888")
        panel3.AddComponent(b, expand='both')
        panel3.Pack()
        panel2.AddComponent(panel3, expand='vertical')

        panel2.Pack()
        self.AddComponent(panel2, expand='b')

        self.Pack()

        # override event for this button
        def my_event(event):
            print "Wahey!"
        b.OnClick = my_event

app = Application(MainFrame, direction='vertical', title="Test test...")
app.MainLoop()
