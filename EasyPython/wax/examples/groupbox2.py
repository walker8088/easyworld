# groupbox2.py
# Works, but note that the order in which you add and pack is *very* tricky.
# Although is not entirely illogical... pack something first, then add it to
# a parent control.  Then pack that one, etc...

from wax import *

TOPPINGS = ('mozzarella', 'gorgonzola', 'pepperoni', 'tomatoes',
            'green peppers')

class MainFrame(Frame):

    def Body(self):
        group = GroupBox(self, text='Toppings', direction='v')
        panel = Panel(group, direction='v')
        for i in range(len(TOPPINGS)):
            s = TOPPINGS[i]
            cb = CheckBox(panel, text=s)
            panel.AddComponent(cb)
        panel.Pack()
        group.AddComponent(panel)
        group.Pack()
        self.AddComponent(group)
        self.Pack()

if __name__ == "__main__":

    app = Application(MainFrame, direction='v')
    app.Run()


