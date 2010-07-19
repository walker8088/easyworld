# gauge-1.py

from wax import *
from wax.tools.gauge import Gauge
import wx

class MainFrame(Frame):
    def Body(self):
        self.counter = 0
        self.panel = Panel(self)
        self.gauge = Gauge(self.panel)
        self.timer = Timer(self, event=self.UpdateProgress)
        self.timer.Start(75)
        
        self.panel.AddComponent(self.gauge, expand='b')
        self.panel.Pack()
        
        self.AddComponent(self.panel, expand='both')
        self.Pack()

    def UpdateProgress(self, event=None):
        self.counter = self.counter + 1
        
        if self.counter >= 100:
            self.counter = 0
        
        self.gauge.SetValue(self.counter)


app = Application(MainFrame)
app.Run()

