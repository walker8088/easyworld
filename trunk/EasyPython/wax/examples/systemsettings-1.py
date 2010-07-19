#
# systemsettings-1.py
#   Demonstrates usage of the SystemSettings class
#     (lots of code taken from the ColourDB wxPython example)
#


from wax import *
import wx

class MetricPanel(ListView):
    def __init__(self, *args, **kwargs):
        ListView.__init__(self, rules='both', columns=['name', 'value'], *args, **kwargs)

        self.metriclist = SystemSettings.GetMetricList()

        for x in self.metriclist:
            self.AppendRow(x, SystemSettings.GetMetric(x))

        self.SetColumnWidth(0, 150)

class FontPanel(ScrollFrame):
    def __init__(self, *args, **kwargs):
        ScrollFrame.__init__(self, *args, **kwargs)
        
        # This could also be done by getting the window's default font;
        # either way, we need to have a font loaded for later on.
        self.SetBackgroundColour(SystemSettings.GetColour("button_face"))

        # Create drawing area
        dc = wx.ClientDC(self)

        # Get the system colors
        self.fontlist = SystemSettings.GetFontList()
        
        # Using GetFullTextExtent(), we calculate a basic 'building block'
        # that will be used to draw a depiction of the color list. We're
        # using 'Wy' as the model becuase 'W' is a wide character and 'y' 
        # has a descender. This constitutes a 'worst case' scenario, which means
        # that no matter what we draw later, text-wise, we'll have room for it
        w,h,d,e = dc.GetFullTextExtent("Wy")
        
        # Height plus descender
        self.textHeight = h + d
        
        # Pad a little bit
        self.lineHeight = self.textHeight + 5

        # ... and this is the basic width.
        self.cellWidth = w

        # Set the scroll bar extents
        self.SetScrollbars(
            self.cellWidth, self.lineHeight, 24, len(self.fontlist) + 2)

    def OnPaint(self, event=None):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        try:
            self.Draw(dc, self.GetUpdateRegion(), self.GetViewStart())
        except:  
            pass

    def Draw(self, dc, rgn=None, vs=None):
        dc.BeginDrawing()
        dc.SetTextForeground("BLACK")
        dc.SetPen(wx.Pen("BLACK", 1, wx.SOLID))
        fonts  = self.fontlist
        numFonts = len(fonts)

        if rgn:
            # determine the subset of the color list that has been exposed 
            # and needs drawn. This is based on all the precalculation we
            # did in __init__()
            rect = rgn.GetBox()
            pixStart = vs[1]*self.lineHeight + rect.y
            pixStop  = pixStart + rect.height
            start = pixStart / self.lineHeight - 1
            stop = pixStop / self.lineHeight
        else:
            start = 0
            stop = numColours

        for line in range(max(0,start), min(stop,numFonts)):
            fnt = fonts[line]
            y = (line+1) * self.lineHeight + 2

            dc.SetFont(SystemSettings.GetFont(fnt))
            dc.DrawText(fnt, self.cellWidth, y)

        dc.EndDrawing()
        
class ColorPanel(ScrollFrame):
    def __init__(self, *args, **kwargs):
        ScrollFrame.__init__(self, *args, **kwargs)
        
        # This could also be done by getting the window's default font;
        # either way, we need to have a font loaded for later on.
        self.SetBackgroundColour(SystemSettings.GetColour("button_face"))
        self.font = Font("Arial", 10)

        # Create drawing area and set its font
        dc = wx.ClientDC(self)
        dc.SetFont(self.font)

        # Get the system colors
        self.clrlist = SystemSettings.GetColorList()
        
        # Using GetFullTextExtent(), we calculate a basic 'building block'
        # that will be used to draw a depiction of the color list. We're
        # using 'Wy' as the model becuase 'W' is a wide character and 'y' 
        # has a descender. This constitutes a 'worst case' scenario, which means
        # that no matter what we draw later, text-wise, we'll have room for it
        w,h,d,e = dc.GetFullTextExtent("Wy")
        
        # Height plus descender
        self.textHeight = h + d
        
        # Pad a little bit
        self.lineHeight = self.textHeight + 5

        # ... and this is the basic width.
        self.cellWidth = w

        # Set the scroll bar extents
        self.SetScrollbars(
            self.cellWidth, self.lineHeight, 24, len(self.clrlist) + 2)

    def OnPaint(self, event=None):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        try:
            self.Draw(dc, self.GetUpdateRegion(), self.GetViewStart())
        except:  
            pass

    def Draw(self, dc, rgn=None, vs=None):
        dc.BeginDrawing()
        dc.SetTextForeground("BLACK")
        dc.SetPen(wx.Pen("BLACK", 1, wx.SOLID))
        dc.SetFont(self.font)
        colours = self.clrlist
        numColours = len(colours)

        if rgn:
            # determine the subset of the color list that has been exposed 
            # and needs drawn. This is based on all the precalculation we
            # did in __init__()
            rect = rgn.GetBox()
            pixStart = vs[1]*self.lineHeight + rect.y
            pixStop  = pixStart + rect.height
            start = pixStart / self.lineHeight - 1
            stop = pixStop / self.lineHeight
        else:
            start = 0
            stop = numColours

        for line in range(max(0,start), min(stop,numColours)):
            clr = colours[line]
            y = (line+1) * self.lineHeight + 2

            dc.DrawText(clr, self.cellWidth, y)

            brush = wx.Brush(SystemSettings.GetColor(clr), wx.SOLID)
            dc.SetBrush(brush)
            dc.DrawRectangle(12 * self.cellWidth, y,
                             6 * self.cellWidth, self.textHeight)

        dc.EndDrawing()
        

class MainFrame(Frame):
    def Body(self):
        nb = NoteBook(self, size=(550, 300))
        cp = ColorPanel(nb)
        fp = FontPanel(nb)
        mp = MetricPanel(nb)

        nb.AddPage(cp, 'System Colors')
        nb.AddPage(fp, 'System Fonts')
        nb.AddPage(mp, 'System Metrics')
        
        self.AddComponent(nb, expand='both')
        self.Pack()

if __name__ == "__main__":
    app = Application(MainFrame, title='SystemSettings Example')
    app.Run()
