# groupbox1.py

from wax import *

TOPPINGS = ('mozzarella', 'gorgonzola', 'pepperoni', 'tomatoes',
            'green peppers')

class MainFrame(Frame):

    def Body(self):
        self.checkboxen = []
        group = GroupBox(self, text='Toppings', direction='v')
        for i in range(len(TOPPINGS)):
            s = TOPPINGS[i]
            cb = CheckBox(group, text=s)
            group.AddComponent(cb)
            self.checkboxen.append(cb)
        group.Pack()
        self.AddComponent(group)

        b = Button(self, 'Order it', event=self.Order)
        self.AddComponent(b, stretch=1, border=2)

        self.Pack()

    def Order(self, event):
        #for cb in self.checkboxen:
        #    if cb.IsChecked():
        #        print cb.GetLabel()
        print "You ordered:",
        print [cb.GetLabel() for cb in self.checkboxen if cb.IsChecked()] \
              or 'no toppings'




if __name__ == "__main__":

    app = Application(MainFrame, direction='v')
    app.Run()

