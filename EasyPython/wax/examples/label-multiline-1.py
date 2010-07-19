# label-multiline-1.py

from wax import *

text = """\
This is a very long text for a label.  It contains line breaks,
so it should stretch over multiple lines.

Yes.

Now for some filler.  These are my favorite languages:

1. Python
2. Lisp
3. Intercal
4. llizard
5. Sheep

Enjoy!
"""

class MainFrame(Frame):
    def Body(self):
        label = Label(self, text)
        self.AddComponent(label, border=10, expand='both')
        self.Pack()
        self.BackgroundColor = label.BackgroundColor = 'white'

app = Application(MainFrame, title='label-multiline-1')
app.Run()
