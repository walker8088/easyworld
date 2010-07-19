# combobox-1.py

from wax import *

CHOICES = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]

class MainFrame(VerticalFrame):

    def Body(self):
        label = Label(self, "Choose your house:")
        self.AddComponent(label, border=3)
        cb1 = ComboBox(self, CHOICES, readonly=1, sort=1)
        self.AddComponent(cb1, expand='h', border=3)
        button = Button(self, "OK", event=self.OnButtonClick)
        self.AddComponent(button, border=3)

        self.Pack()

        self.BackgroundColor = label.BackgroundColor = 'white'
        self.cb1 = cb1

    def OnButtonClick(self, event):
        print "You chose:", self.cb1.GetValue()

app = Application(MainFrame, resize=0)
app.Run()
