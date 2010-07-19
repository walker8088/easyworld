# xrc-1.py

import wax.tools.waxrf as waxrf
from wax import *

resource = """\
<?xml version="1.0" ?>
<resource>
  <object class="Panel" name="mypanel">
    <object class="wxBoxSizer">
      <object class="sizeritem" expand="both" border="5">
        <object class="wxButton">
          <label>Click Me!</label>
        </object>
      </object>
    </object>
  </object>
</resource>
"""

# /\---------
# Compare the two, and see how Wax can make your life easier! :)
# ---------\/

resource = """\
<?xml version="1.0" ?>
<resource>
  <Panel name="mypanel">
    <Button name="mybutton" text="Click Me!" expand="both" border="5" />
  </Panel>
</resource>
"""


res = waxrf.XMLResource()
res.LoadFromFile('test.waxrf')

class MainFrame(VerticalFrame):
    def Body(self):
        self.dlg = res.LoadDialog(self, 'mydialog')
        res.LoadMenuBar(self, 'mb')
        
        p1 = res.LoadPanel(self, 'p1')
        b = Button(self, text='Show Dialog', event=self.button)

        self.AddComponent(p1, expand='both')
        self.AddComponent(b, expand='h', border=5)
        self.Pack()

    def button(self, event=None):
        self.dlg.ShowModal()

app = Application(MainFrame, title='Wax XRC Example')
app.Run()
