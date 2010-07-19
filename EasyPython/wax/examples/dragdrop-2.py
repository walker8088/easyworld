# dragdrop-2.py
#   Demonstrates giving DnD capabilities to controls and
#   how to use the Clipboard
#
# Original by Jason Gedge.  Modifications by Hans Nowak.

from wax import *

# One way to use *DropTargets is to override OnDropFiles or OnDropText.
            
class MyFileDropTarget(FileDropTarget):
    def OnDropFiles(self, x, y, files):
        tb = self.window.tb
        tb.AppendText('Received:\n')
        for file in files:
            tb.AppendText('  - ')
            tb.AppendText(file.strip())
            tb.AppendText('\n')

class MyTextDropTarget(TextDropTarget):
    def OnDropText(self, x, y, text):
        tb = self.window.tb
        res, row, col = tb.HitTest((x, y))
        tb.InsertText(tb.XYToPosition(row, col), text)

    def OnDragOver(self, x, y, d):
        row, col, tb = 0, 0, self.window.tb
        res, row, col = tb.HitTest((x, y))
        tb.SetInsertionPoint(tb.XYToPosition(row, col))
        return TextDropTarget.OnDragOver(self, x, y, d)

class URLDropPanel(VerticalPanel):

    def __init__(self, *args, **kwargs):
        VerticalPanel.__init__(self, *args, **kwargs)

        lbl = Label(self, text='Drag a URL to the window below to load that URL')
        
        # Another way to use *DropTarget is to pass in an event.
        td = URLDropTarget(self, event=self.LoadURL)
        self.htmlwin = HTMLWindow(self)

        self.AddComponent(lbl, expand='h', border=5)
        self.AddComponent(self.htmlwin, expand='both', border=5)
        self.Pack()
        
    def LoadURL(self, x, y, d, url):
        print "** Loading:", url
        self.htmlwin.LoadPage(url)

    def tb_OnChar(self, event=None):
        pass

class FileDropPanel(VerticalPanel):
    def __init__(self, *args, **kwargs):
        VerticalPanel.__init__(self, *args, **kwargs)

        lbl = Label(self, text='Drag some files into the box below')

        td = MyFileDropTarget(self)
        self.tb = TextBox(self, size=(300,300), multiline=1, hscroll=1)
        self.tb.OnChar = self.tb_OnChar

        self.AddComponent(lbl, expand='h', border=5)
        self.AddComponent(self.tb, expand='both', border=5)
        self.Pack()

    def tb_OnChar(self, event=None):
        pass

class TextDropPanel(VerticalPanel):
    def __init__(self, *args, **kwargs):
        VerticalPanel.__init__(self, *args, **kwargs)

        lbl = Label(self, text='Type some text below and then\ndrag some other text into it!')

        td = MyTextDropTarget(self)
        self.tb = TextBox(self, size=(300,300), multiline=1)

        btn_copy = Button(self, text='Copy Text From Above', event=self.copy_OnClick)
        btn_paste = Button(self, text='Paste Text From Above', event=self.paste_OnClick)

        self.AddComponent(lbl, expand='h', border=5)
        self.AddComponent(self.tb, expand='both', border=5)
        self.AddComponent(btn_copy, expand='h', border=2)
        self.AddComponent(btn_paste, expand='h', border=2)
        self.Pack()

    def copy_OnClick(self, event=None):
        Clipboard.SetText(self.tb.GetStringSelection())

    def paste_OnClick(self, event=None):
        cliptext = Clipboard.GetText()
        if cliptext != "":
            sel = self.tb.GetSelection()
            self.tb.Replace(sel[0], sel[1], cliptext)

class MainFrame(Frame):
    def Body(self):
        nb = NoteBook(self, size=(300,300))
        p1 = TextDropPanel(nb)
        p2 = FileDropPanel(nb)
        p3 = URLDropPanel(nb)
        nb.AddPage(p1, 'Text')
        nb.AddPage(p2, 'File')
        nb.AddPage(p3, 'Text (URL)')
        self.AddComponent(nb, expand='both')
        self.Pack()

if __name__ == "__main__":
    app = Application(MainFrame, title='Drag/Drop Example')
    app.Run()
