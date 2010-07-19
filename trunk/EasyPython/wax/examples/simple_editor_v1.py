# simple_editor.py

from wax import *

FIXED_FONT = ('Courier New', 10)

class MainFrame(Frame):

    def Body(self):
        self.filename = None
        self.CreateMenu()
        self.textbox = TextBox(self, multiline=1, wrap=0)
        self.textbox.SetFont(FIXED_FONT)
        self.AddComponent(self.textbox)

    def CreateMenu(self):
        menubar = MenuBar()

        menu1 = Menu(self)
        menu1.Append("&New", self.New, "Create a new file")
        menu1.Append("&Open", self.Open, "Open a file")
        menu1.Append("&Save", self.Save, "Save a file")

        menubar.Append(menu1, "&File")

        self.SetMenuBar(menubar)

    def New(self, event):
        self.textbox.Clear()
        self.filename = None

    def Open(self, event):
        dlg = FileDialog(self, open=1)
        try:
            result = dlg.ShowModal()
            if result == 'ok':
                filename = dlg.GetPaths()[0]
                self._OpenFile(filename)
        finally:
            dlg.Destroy()

    def _OpenFile(self, filename):
        self.filename = filename
        f = open(filename, 'r')
        data = f.read()
        f.close()
        self.textbox.Clear()
        self.textbox.AppendText(data)

    def Save(self, event):
        if self.filename:
            self._SaveFile(self.filename)
        else:
            dlg = FileDialog(self, save=1)
            try:
                result = dlg.ShowModal()
                if result == 'ok':
                    filename = dlg.GetPaths()[0]
                    self.filename = filename
                    self._SaveFile(filename)
            finally:
                dlg.Destroy()

    def _SaveFile(self, filename):
        f = open(filename, 'w')
        f.write(self.textbox.GetValue())
        f.close()

app = Application(MainFrame, title="A simple editor")
app.Run()
