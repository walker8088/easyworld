# spinbox-1.py
# By Daniel James Baker.  Minor modifications by Hans Nowak.
# Requires Wax 0.3.13 or better.

from wax import *
from wax.tools.spinbox import SpinBox

class MainFrame(Frame):
    def DoChoice(self, event=None):
        FUNCTIONS = [lambda: self.sb1.SetValue(30), 
                     self.sb1.GetValue,
                     lambda: self.sb1.SetMax(200), 
                     lambda: self.sb1.SetMin(-40),
                     lambda: self.sb1.SetRange(0,100), 
                     self.sb1.GetMax,
                     self.sb1.GetMin, 
                     self.sb1.GetRange]
        selection = self.ddb.GetSelection()
        if selection != -1:
            result = FUNCTIONS[selection]()
            self.tb.write(self.CHOICES[selection] + ' called\n')
            if selection in [1, 5, 6, 7]: # Get function called
                self.tb.write('Result = ' + str(result) + '\n')

    def Spin_sb1(self, event=None):
        self.tb.write('Spin event\n')
        if event is not None:
            event.Skip() # We do this to make sure OnSpinCtrl is also called

    def Body(self):
        self.CHOICES = ['SetValue(30)', 'GetValue()', 'SetMax(200)', 
                        'SetMin(-40)', 'SetRange(0,100),', 'GetMax()', 
                        'GetMin()', 'GetRange()']
        p1 = Panel(self)
        self.sb1 = SpinBox(p1) # "plain" box, no arrow keys or wrap
        # Event handlers - just write an appropriate message to the log box
        self.sb1.OnSpinCtrl = lambda event: self.tb.write('SpinCtrl event\n')
        self.sb1.OnText = lambda event: self.tb.write('Text event\n')
        self.sb1.OnSpin = self.Spin_sb1
        self.sb1.OnSpinUp = lambda event: self.tb.write('SpinUp event\n')
        self.sb1.OnSpinDown = lambda event: self.tb.write('SpinDown event\n')
        p1.AddComponent(self.sb1)
        self.tb = TextBox(p1, multiline=1, wrap=0, readonly=1) # log box for events
        p1.AddComponent(self.tb, expand='both')
        self.ddb = DropDownBox(p1, self.CHOICES)
        p1.AddComponent(self.ddb)
        b = Button(p1, 'Do it', event=self.DoChoice)
        p1.AddComponent(b)
        p1.Pack()
        
        p2 = Panel(self)
        sb2 = SpinBox(p2, arrowkeys=1) # arrow keys enabled
        l2 = Label(p2, "SpinBox with arrow keys enabled")
        p2.AddComponent(sb2)
        p2.AddComponent(l2)
        p2.Pack()

        p3 = Panel(self)
        sb3 = SpinBox(p3, wrap=1) # wraparound enabled
        l3 = Label(p3, "SpinBox with wraparound enabled")
        p3.AddComponent(sb3)
        p3.AddComponent(l3)
        p3.Pack()

        self.AddComponent(p1, expand='both')
        self.AddComponent(p2, expand='h')
        self.AddComponent(p3, expand='h')
        self.Pack()

app = Application(MainFrame, title='spinbox-1', direction='vertical')
app.Run()
