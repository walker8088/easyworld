# check-parent-warning-1.py

from wax import *

WaxConfig.check_parent = 1

class MainFrame(Frame):
    def Body(self):
        self.nb = NoteBook(self)
        self.AddComponent(self.nb, expand='both')

        self.Pack()

        self.OpenFirstPage()

    def OpenFirstPage(self):
        sp = Splitter(self) # wrong parent! this causes an exception
        tb1 = TextBox(sp)
        tb2 = TextBox(sp, "and more there")
        sp.Split(tb1, tb2, direction='h')
        self.nb.AddPage(sp, "Page 1")
        tb1.Value = 'some text here'



app = Application(MainFrame)
app.Run()
