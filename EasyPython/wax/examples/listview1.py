# listview1.py

from wxPython.wx import *
from wax import *

class MainFrame(Frame):
    def Body(self):
        listview = ListView(self, size=(500,300), rules='both',
                   columns=["Sender", "Subject", "Date"])

        for i in range(100):
            listview.InsertStringItem(i, `i`)
            listview.SetStringItem(i, 0, "sender" + str(i))
            listview.SetStringItem(i, 1, "subject" + str(i))
            listview.SetItemData(i, i)

        # but, we're better off using InsertRow...
        listview.InsertRow(100, "Hans Nowak", "Problems with wxPython", "2003-05-29 12:42:00")

        # or maybe AppendRow...
        listview.AppendRow("Fred", "Re: Problems with wxPython", "?")

        # __setitem__...
        listview[0,0] = "Dookie"
        listview[0,1] = "Re: Programming"
        print listview[1,1]
        listview[110,0] = "Bjorn Lassing"
        listview[111,0] = 42     # number is converted to string
        listview[111,1] = {1:2}  # ditto for dict
        listview[111,2] = u'an unicode string'  # remains as it is

        listview.SetColumnWidth(0, 150)
        listview.SetColumnWidth(1, 200)

        # set some events...
        listview.OnItemSelected = self.OnListItemSelected
        listview.OnItemDoubleClick = self.OnListItemDoubleClick

        self.AddComponent(listview, expand=1, stretch=1)
        self.Pack()

    def OnListItemSelected(self, event=None):
        listview = event.GetEventObject()
        currentitem = event.m_itemIndex
        print listview.GetItemText(currentitem)

    def OnListItemDoubleClick(self, event=None):
        listview = event.GetEventObject()
        currentitem = event.m_itemIndex
        print "You double-clicked:", listview.GetItemText(currentitem)


app = Application(MainFrame)
app.MainLoop()
