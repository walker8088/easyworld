# bitmap-2.py
# Bitmap and label.

from wax import *

class MainFrame(VerticalFrame):
    def Body(self):
        jpg = Image('moo.jpg')
        bitmap = jpg.ConvertToBitmap()
        bmp = Bitmap(self, bitmap)
        self.AddComponent(bmp)

        label = Label(self, "When cows converse...")
        self.AddComponent(label, expand='h', border=5)
        label.BackgroundColor = self.BackgroundColor = 'white'

        self.Pack()

app = Application(MainFrame, title='bitmap-2')
app.Run()
