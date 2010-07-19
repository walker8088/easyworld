# bitmap1.py
# Finally we manage to load and display an image.  What a pain.
# Two issues:
# 1. path needs to be correct (use \\ on Windows rather than /, for example)
# 2. the appropriate handler for the image type needs to be installed (Image
#    takes care of this automagically)

from wax import *

class MainFrame(Frame):
    def Body(self):
        jpg = Image('moo.jpg')
        bitmap = jpg.ConvertToBitmap()
        bmp = Bitmap(self, bitmap)
        self.AddComponent(bmp)
        self.Pack()


app = Application(MainFrame)
app.MainLoop()
