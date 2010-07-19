# treelistview-1.py

from wax import *
import wx
# uses wx at the moment; will be fixed later

class MainFrame(Frame):

    def CreateTreeListView(self, parent):
        treelistview = TreeListView(parent,
                       columns=["Main column", "Column 1", "Column 2"],
                       has_buttons=0, lines=0)
        treelistview.Size = (400, 400)

        # add columns
        treelistview.SetMainColumn(0)
        treelistview.SetColumnWidth(0, 175)

        isz = (16, 16)
        il = ImageList(*isz)
        ifolder = il.Add(wx.ArtProvider_GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, isz))
        iopen = il.Add(wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN, wx.ART_OTHER, isz))
        print ifolder, iopen
        treelistview.SetImageList(il)
        self.il = il

        self.root = treelistview.AddRoot("the root item")
        treelistview.SetItemText(self.root, "col 1 root", 1)
        treelistview.SetItemText(self.root, "col 2 root", 2)
        treelistview.SetItemImage(self.root, ifolder, which=wx.TreeItemIcon_Normal)
        treelistview.SetItemImage(self.root, iopen, which=wx.TreeItemIcon_Expanded)

        for x in range(15):
            text = "Item %d" % (x,)
            child = treelistview.AppendItem(self.root, text)
            # child is a TreeItemId or something like that :-(
            treelistview.SetItemText(child, text + "(c1)", 1)
            treelistview.SetItemText(child, text + "(c2)", 2)
            treelistview.SetItemImage(child, ifolder, which=wx.TreeItemIcon_Normal)
            treelistview.SetItemImage(child, iopen, which=wx.TreeItemIcon_Expanded)
            # this should really be something like:
            # child.SetText(column, text)
            # or even:
            # child[column] = text
            # ...can we use a wrapper object without messing up everything?

            for y in range(5):
                text = "Item %d-%d" % (x, y)
                last = treelistview.AppendItem(child, text)
                treelistview.SetItemText(last, text + "(c1)", 1)
                treelistview.SetItemText(last, text + "(c1)", 1)
                treelistview.SetItemImage(last, ifolder, which=wx.TreeItemIcon_Normal)
                treelistview.SetItemImage(last, iopen, which=wx.TreeItemIcon_Expanded)

        return treelistview

    def Body(self):
        self.treelistview = self.CreateTreeListView(self)
        self.AddComponent(self.treelistview, expand='both')
        self.Pack()

app = Application(MainFrame)
app.Run()
