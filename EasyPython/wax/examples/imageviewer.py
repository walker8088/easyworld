# imageviewer.py

from wax import *
import sys

try:
    filename = sys.argv[1]
except IndexError:
    print "Usage: imageviewer.py filename"
    raise SystemExit

class MainFrame(Frame):
    def Body(self):
        self.SetTitle("Image Viewer")
        bitmap = Image(sys.argv[1]).ConvertToBitmap()
        # we use AddComponent and Pack here, so the image doesn't stretch
        self.AddComponent(Bitmap(self, bitmap))
        self.Pack()


app = Application(MainFrame)
app.MainLoop()
