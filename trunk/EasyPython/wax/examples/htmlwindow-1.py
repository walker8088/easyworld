# htmlwindow-1.py
# Very simple demo of HTMLWindow.

from wax import *

HTML = """\
<h3>HTMLWindow</h3>

<p>Hello friends! This is some simple <b>HTML</b>.</p>

<p>Flourish &amp; Blotts</p>

<p>Also visit <a href="http://www.python.org/">www.python.org</a>!</p>
"""

class MainFrame(Frame):

    def Body(self):
        self.htmlwindow = HTMLWindow(self)
        self.AddComponent(self.htmlwindow, expand=1, stretch=1)
        self.Pack()
        self.Size = (500, 400)

        self.htmlwindow.AppendToPage(HTML)

app = Application(MainFrame, title='htmlwindow-1.py')
app.Run()
