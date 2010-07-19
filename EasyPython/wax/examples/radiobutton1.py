# radiobutton1.py

from wax import *

CRUSTS = ['pan crust', 'hand-tossed', 'stuffed', 'crispy']

class MainFrame(Frame):

    def Body(self):
        label = Label(self, text="Select a pizza crust:")
        self.AddComponent(label, border=5)

        for s in CRUSTS:
            rb = RadioButton(self, s)
            self.AddComponent(rb, border=2)

        b = Button(self, "Order", event=self.Order)
        self.AddComponent(b, border=5)

        self.SetBackgroundColour(rb.GetBackgroundColour())

        self.Pack()

    def Order(self, event):
        for obj in self.GetChildren():
            if isinstance(obj, RadioButton) and obj.GetValue():
                print "You selected:", obj.GetLabel()


if __name__ == "__main__":

    app = Application(MainFrame, direction='v')
    app.Run()

