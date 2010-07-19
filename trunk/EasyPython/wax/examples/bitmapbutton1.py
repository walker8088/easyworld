# bitmapbutton1.py

from wax import *

class MainFrame(Frame):

    def Body(self):
        # we're using an icon as bitmap, so install the correct image handler
        AddImageHandler('ico')
        # create some buttons
        bb1 = BitmapButton(self, 'heretic2.ico', event=self.Blah)
        self.AddComponent(bb1, border=5)
        # grr, no label can be displayed

        self.Pack()

    def Blah(self, event):
        print "Clickety-click"

if __name__ == "__main__":

    app = Application(MainFrame, title='bitmapbutton1', direction='v')
    app.Run()

