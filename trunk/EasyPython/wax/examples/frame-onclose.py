# frame-onclose.py
# Overriding Frame.OnClose.
# Note that "creating HelpWindow" is only called once, while "hiding" is
# called whenever the window is "closed" (actually hidden).

from wax import *

html = """
<h3>Help window</h3>

<p>Sample help text here...</p>

<p>Another paragraph...</p>
"""

class HelpWindow(Frame):
    def Body(self):
        print 'creating HelpWindow...'
        self.htmlwindow = HTMLWindow(self)
        self.AddComponent(self.htmlwindow, expand='both')
        self.htmlwindow.SetPage(html)
        self.Pack()
        self.Size = (300, 300)
    def Display(self):
        self.Show()
        self.SetFocus()
    def OnClose(self, event):
        print 'hiding HelpWindow...'
        self.Hide()
        # note that we don't call event.Skip(), so nothing is actually closed!

class MainFrame(Frame):

    def Body(self):
        self.helpwindow = HelpWindow(self, title="Help window")
        b = Button(self, "Show help window", event=self.OnShowHelp)
        self.AddComponent(b, expand='b', border=5)
        self.Pack()
        self.Size = (100, 100)

    def OnShowHelp(self, event):
        self.helpwindow.Display()

app = Application(MainFrame, title='frame-onclose')
app.Run()
