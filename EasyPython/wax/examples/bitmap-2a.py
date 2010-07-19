# bitmap-2a.py
# Bitmap and label in a flexgrid.

from wax import *

class MainFrame(VerticalFrame):
    def Body(self):
        fgp = FlexGridPanel(self, 2, 2, 10, 10)
        count = 0
        for i in range(2):
            for j in range(2):
                count = count + 1
                p = self.MakePicturePanel(fgp, count)
                fgp.AddComponent(j, i, p)
        fgp.Pack()
        self.AddComponent(fgp, expand='b', border=10)
        self.Pack()

    def MakePicturePanel(self, parent, number):
        p = VerticalPanel(parent)
        jpg = Image('moo.jpg')
        bitmap = jpg.ConvertToBitmap()
        bmp = Bitmap(p, bitmap)
        p.AddComponent(bmp)

        label = Label(p, "Numbuh " + str(number))
        p.AddComponent(label, expand='h', border=5)
        label.BackgroundColor = self.BackgroundColor = 'white'

        p.Pack()
        return p

app = Application(MainFrame, title='bitmap-2a')
app.Run()
