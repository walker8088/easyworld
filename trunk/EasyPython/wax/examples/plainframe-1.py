# plainframe-1.py
# Demonstrates how to use a PlainFrame control.  (Simply add controls to it
# at a given position.  Size can be set too.)

from wax import *

WaxConfig.check_parent = True

class MainFrame(PlainFrame):

    def Body(self):
        self.SetSize((400, 400))
        b = Button(self, "Button 0")
        bx, by = b.GetSize()
        print "Size of a regular button:", (bx, by)
        self.AddComponent(10, 10, b)

        x = 10
        y = 10
        for i in range(5):
            x += 10
            y += by
            b = Button(self, "Button " + str(i+1))
            self.AddComponent(x, y, b)

        text = TextBox(self, text="blah-blah",multiline=1)
        self.AddComponentAndSize(200, 20, 150, 100, text)

app = Application(MainFrame, title='plain as folk')
app.Run()
