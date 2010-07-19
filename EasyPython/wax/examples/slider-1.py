# slider-1.py

from wax import *
from wax.tools.slider import Slider

class MainFrame(Frame):
    def Body(self):
        self.hpanel = HorizontalPanel(self)
        self.vpanel = VerticalPanel(self)
        
        self.slider1 = Slider(self.vpanel, labels=1, event=self.OnScroll)
        self.slider2 = Slider(self.vpanel, ticks='t')
        self.vpanel.AddComponent(self.slider1, expand='h', border=5)
        self.vpanel.AddComponent(self.slider2, expand='h', border=5)
        self.vpanel.Pack()
        
        self.slider3 = Slider(self.hpanel, ticks='r')
        self.slider4 = Slider(self.hpanel, ticks='l')
        self.hpanel.AddComponent(self.slider3, expand='v', border=5)
        self.hpanel.AddComponent(self.slider4, expand='v', border=5)
        self.hpanel.Pack()
        
        self.AddComponent(self.vpanel, expand='both')
        self.AddComponent(self.hpanel, expand='both')
        self.Pack()
        self.SetSize((400, 200))

    def OnScroll(self, event=None):
        print event.GetPosition()

app = Application(MainFrame, title='slider-1')
app.Run()

