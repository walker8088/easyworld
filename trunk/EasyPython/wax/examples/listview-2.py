# listview-2.py

from wax import *

COLUMNS = ["one", "two", "three", "four", "five"]
COLORS = ["yellow", "white", "pink", "#FFFFE0", "light blue", "peachpuff"]

class MyVirtualListView(ListView):
    def __init__(self, parent, **rest):
        ListView.__init__(self, parent, columns=COLUMNS, virtual=1, 
                          rules='both', **rest)
        self.SetItemCount(10000)
        
        self.attrs = []
        for color in COLORS:
            attr = ListItemAttr()
            attr.SetBackgroundColor(color)
            self.attrs.append(attr)
        
    def OnGetItemText(self, item, col):
        return "%d, %s" % (item, COLUMNS[col])
    def OnColumnClick(self, event):
        print "Aha, you clicked column", event.GetColumn(),
        print "(%r)" % (COLUMNS[event.GetColumn()],)
    def OnGetItemAttr(self, row):
        idx = row % len(COLORS)
        attr = self.attrs[idx]
        return attr
        

class MainFrame(Frame):
    def Body(self):
        self.listview = MyVirtualListView(self)
        self.AddComponent(self.listview, expand='b')
        self.Pack()
        
        self.Size = (500, 400)
        
if __name__ == "__main__":

    app = Application(MainFrame, title='listview-2')
    app.Run()
    