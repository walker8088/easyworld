# fancylabel-1.py

from wax import *
from wax.tools.fancylabel import FancyLabel

text = """<font family="swiss" color="dark green" size="40">FANCY</font>
<font family="decorative" color="red" size="20" style="italic">LABEL</font>"""

class MainFrame(Frame):
    def Body(self):
        p = VerticalPanel(self)
        fancy = FancyLabel(p, text)
        label = Label(p, "This is just a regular label")

        p.AddComponent(fancy, expand='b')
        p.AddComponent(label, expand='h', border=5)
        p.Pack()

        self.AddComponent(p, expand='b', border=5)
        self.Pack()


if __name__ == "__main__":
    app = Application(MainFrame, title='test test...', direction='v')
    app.Run()