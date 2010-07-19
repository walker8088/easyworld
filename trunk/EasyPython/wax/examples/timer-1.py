# timer-1.py

from wax import *

class MainFrame(Frame):

    def Body(self):
        self.label = Label(self, '...')
        self.AddComponent(self.label, border=20)
        self.Pack()

        self.SetBackgroundColor('white')
        self.label.SetBackgroundColor('white')

        self.count = 0

        core.DEBUG = 1
        timer = Timer(self, event=self.IncCount)
        timer.Start(1000)

    def IncCount(self, event):
        self.count += 1
        self.label.SetLabel(str(self.count))
        if self.count > 10:
            self.Close()

app = Application(MainFrame)
app.Run()
