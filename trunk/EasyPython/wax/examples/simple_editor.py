# simple_editor.py

from wax import *

FIXED_FONT = ('Courier New', 10)

class MainFrame(Frame):

    def Body(self):
        self.filename = None
        self.CreateMenu()

        toolbar = self.CreateToolbar(self)
        self.AddComponent(toolbar, expand='h')

        self.textbox = TextBox(self, multiline=1, wrap=0)
        self.textbox.SetFont(FIXED_FONT)
        self.textbox.SetSize((600,400))
        self.AddComponent(self.textbox, expand='both')

        self.Pack()

        self.statusbar = StatusBar(self, numpanels=2)
        self.SetStatusBar(self.statusbar)

    def CreateMenu(self):
        menubar = MenuBar()

        menu1 = Menu(self)
        menu1.Append("&New", self.New, "Create a new file", hotkey="Ctrl-N")
        menu1.Append("&Open", self.Open, "Open a file", hotkey="Ctrl-O")
        menu1.Append("&Save", self.Save, "Save a file", hotkey="Ctrl-S")

        menubar.Append(menu1, "&File")

        self.SetMenuBar(menubar)

    def CreateToolbar(self, parent):
        p = Panel(parent, direction='horizontal')
        p.AddComponent(Button(p, "New", self.New))
        p.AddComponent(Button(p, "Open", self.Open))
        p.AddComponent(Button(p, "Save", self.Save))
        p.Pack()
        return p

    def New(self, event):
        self.textbox.Clear()
        self.SetFilename(None)

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
        self.SetFilename(filename)
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
                    self.SetFilename(filename)
                    self._SaveFile(filename)
            finally:
                dlg.Destroy()

    def _SaveFile(self, filename):
        f = open(filename, 'w')
        f.write(self.textbox.GetValue())
        f.close()

    def SetFilename(self, filename):
        self.filename = filename
        self.statusbar[1] = "Filename: " + str(self.filename)

app = Application(MainFrame, title="A simple editor", direction='vertical')
app.Run()
