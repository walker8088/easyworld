# statusbar-1.py

from wax import *
import time

class MainFrame(VerticalFrame):
    def Body(self):
        statusbar = StatusBar(self, numpanels=3, add=1)
        # "add=1" adds the statusbar to its parent automagically; if you omit
        # this, you'll have to do self.SetStatusBar(statusbar) explicitly

        # add some buttons so the window isn't so empty
        for i in range(5):
            b = Button(self, str(i+1))
            self.AddComponent(b, expand='h')

        self.Pack()
        self.SizeX = 400

        # let's put some text in that status bar
        statusbar[0] = "hello"
        statusbar[1] = time.asctime(time.localtime())
        statusbar[2] = "foo!"

app = Application(MainFrame)
app.Run()
