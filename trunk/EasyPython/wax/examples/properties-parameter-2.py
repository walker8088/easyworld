# properties-parameter-2.py

from wax import *

class MainFrame(PlainFrame):
    def Body(self):
        myfont = Font("Tahoma", 8, bold=1)

        # pseudo-properties can now be set in the constructor...
        label = Label(self, "Hello", Font=myfont, Position=(10,10),
                     ForegroundColor='red', BackgroundColor='white')
        button = Button(self, "Dummy", Position=(20,70), SizeX=130,
                 BackgroundColor='peachpuff', event=self.OnClickButton)

        self.Pack()
        self.Size = 200, 200
    def OnClickButton(self, event):
        obj = event.GetEventObject()
        print "foobar is:", obj.foobar

app = Application(MainFrame)
app.Run()
