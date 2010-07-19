# listbox1.py

from wax import *

LIST1 = sys.modules.keys()
LIST1.sort()

import keyword
LIST2 = keyword.kwlist

import __builtin__
LIST3 = __builtin__.__dict__.keys()
LIST3.sort()

def clicked(event):
    print "Clicked:", event.GetEventObject()

class MainFrame(Frame):
    def Body(self):
        # the panel isn't really necessary, but we can use it to add a border
        p1 = Panel(self, direction='h')
        listbox1 = ListBox(p1, choices=LIST1, size=(120, 150), selection='single')
        p1.AddComponent(listbox1, border=3, expand='both')
        listbox2 = ListBox(p1, choices=LIST2, size=(120, 150), selection='multiple')
        p1.AddComponent(listbox2, border=3, expand='both')
        listbox3 = ListBox(p1, choices=LIST3, size=(120, 150), selection='extended',
                   horizontal_scrollbar=1) # visible on Windows only
        p1.AddComponent(listbox3, border=3, expand='both')
        p1.Pack()

        listbox1.OnClick = listbox2.OnClick = listbox3.OnClick = clicked

        self.AddComponent(p1, border=5, expand='both')
        self.Pack()

if __name__ == "__main__":

    app = Application(MainFrame, title='blah', direction='v')
    app.Run()

