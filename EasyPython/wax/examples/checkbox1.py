# checkbox1.py

from wax import *

toppings = ['mozzarella', 'tomatoes', 'pepperoni', 'green peppers', 'bacon']

class MainFrame(Frame):

    def Body(self):
        label = Label(self, "Select your toppings:")
        self.AddComponent(label, border=5)

        # use a panel for better layout of the checkboxes
        p = Panel(self, direction='v')

        for s in toppings:
            cb = CheckBox(p, s)
            cb._value = s   # we just stick a value in it
            p.AddComponent(cb)

        limcb = CheckBox(p, "Limburger", border=0)   # no visible difference?
        limcb._value = "Limburger"
        limcb.OnCheck = self.OnCheckLimburger
        p.AddComponent(limcb)

        p.Pack()
        self.AddComponent(p, border=3)
        self.panel = p

        b = Button(self, "Order", event=self.Order)
        self.AddComponent(b, border=5)

        # colors are out of whack on Windows; fix them
        self.SetBackgroundColour(limcb.GetBackgroundColour())
        label.SetBackgroundColour(limcb.GetBackgroundColour())

        self.Pack()

    def OnCheckLimburger(self, event):
        if event.GetEventObject().IsChecked():
            print "It's really very runny, sir."
        else:
            print "We were out of it anyway."

    def Order(self, event=None):
        print "You want these toppings:"
        for obj in self.panel.GetChildren():
            if isinstance(obj, CheckBox) and obj.IsChecked():
                print obj._value

if __name__ == "__main__":

    app = Application(MainFrame, direction='v')
    app.Run()

