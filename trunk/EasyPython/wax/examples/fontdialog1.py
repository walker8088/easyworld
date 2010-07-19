# fontdialog1.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        p = Panel(self, direction='h')
        b = Button(p, "Select font...", self.SelectFont)
        p.AddComponent(b)
        p.Pack()
        self.AddComponent(p, stretch=1, border=1)

        self.label = Label(self, "Jackdaws love my big sphinx of quartz.", align='center')
        self.label.SetSize((400, 100))
        self.AddComponent(self.label, stretch=1, expand=1, border=5)

        self.Pack()

        # some test code... will remove later
        #
        font = self.label.GetFont() # a wax Font, not a wxFont!
        print ">>", font
        #print ">>", font.IsBold(), font.IsItalic()  # wrong!
        print ">>", dir(font)
        #

    def SelectFont(self, event):
        dlg = FontDialog(self)
        try:
            if dlg.ShowModal() == 'ok':
                data = dlg.GetFontData()
                font = data.GetChosenFont()
                self.label.SetFont(font)
                #self.Refresh()
        finally:
            dlg.Destroy()


app = Application(MainFrame, direction='v')
app.Run()
