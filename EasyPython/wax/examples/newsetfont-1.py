# newsetfont-1.py
# Test the new SetFont functionality (new as of 0.2.22.)
# Also demonstrates the WaxObject.SetAttributes method.

from wax import *

WaxConfig.default_font = ("Verdana", 10)

class MainFrame(Frame):
    def Body(self):
        b1 = Button(self, "A button")
        self.AddComponent(b1, expand='h')
        b2 = Button(self, "Another button")
        b2.Font = ("Courier New", 10)
        # tuples can be passed to SetFont now too!
        self.AddComponent(b2, expand='h')
        b3 = Button(self, "A third button")
        b3.SetAttributes(BackgroundColor='yellow', Font=("Tahoma", 8))
        self.AddComponent(b3, expand='h')

        self.Pack()

app = Application(MainFrame, direction='v')
app.Run()
