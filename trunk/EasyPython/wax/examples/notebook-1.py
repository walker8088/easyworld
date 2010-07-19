# notebook-1.py

from wax import *

COLORS = ['white', 'red', 'blue', 'yellow', 'ivory', 'peachpuff', 'bisque',
          'aquamarine', 'salmon']

class MainFrame(Frame):
    def Body(self):
        self.nb = NoteBook(self)
        self.nb.Size = (400,200)
        self.AddComponent(self.nb, expand='both')

        for color in COLORS:
            self.CreatePage(color)

        self.Pack()

    def CreatePage(self, color):
        textbox = TextBox(self.nb)
        textbox.SetBackgroundColor(color)
        textbox.write(color)
        self.nb.AddPage(textbox, color)

app = Application(MainFrame)
app.Run()
