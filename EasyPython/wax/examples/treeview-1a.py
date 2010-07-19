# treeview1.py

from wax import *

twist_buttons = 1
# set to 1 to show Mac-style buttons... if your system supports them

def filltree(tree):
    root = tree.AddRoot("the root item")
    for i in range(10):
        child = tree.AppendItem(root, "Item %d" % (i,))
        for j in range(5):
            grandchild = tree.AppendItem(child, "Item %d" % (i*10+j))

    print [x for x in tree.GetChildNodes(root)]

    d = [
        ["Hans", None, [
            ["age", 30, []],
            ["sign", "Aquarius", []],
            ["job", "programmer", []],
        ]],
        ["Fred", None, [
            ["age", "unknown", []],
            ["sign", "unknown", []],
            ["shoe size", "unknown", []],
        ]],
        ["Old Guy John", None, [
            ["age", "old", []],
            ["sign", "Aquarius", []],
        ]],
        ["Bob", None, [
            ["sign", "Taurus", []],
            ["job", "proprietor", []],
        ]],
        ["Christine", None, [
            ["age", 17, []],
            ["sign", "Aries", []],
            ["job", "cashier", []],
        ]],
    ]

    stuff = tree.AppendItem(root, "stuff")
    tree.LoadFromNestedList(stuff, d)

    return tree

class MainFrame(Frame):

    def Body(self):
        splitter = Splitter(self, size=(500, 300))
        self.treeview = TreeView(splitter, twist_buttons=twist_buttons, has_buttons=1)
        self.treeview.OnSelectionChanged = self.OnTreeSelectionChanged
        self.textbox = TextBox(splitter, multiline=1)
        splitter.Split(self.treeview, self.textbox, direction='v')
        self.AddComponent(splitter, expand='both')
        filltree(self.treeview)
        self.Pack()

    def OnTreeSelectionChanged(self, event):
        item = event.GetItem()
        data = self.treeview.GetPyData(item)
        if data is None:
            data = self.treeview.GetItemText(item)
        self.textbox.Clear()
        self.textbox.AppendText(str(data))
        event.Skip()

app = Application(MainFrame, direction='h')
app.Run()
