# business-1.py

from wax import *

CRUSTS = ["pan", "hand-tossed", "garlic butter", "thin && crispy", "stuffed"]
TOPPINGS = ["mozzarella", "gorgonzola", "anchovies", "pepperoni",
            "sausage", "peppers", "beef", "ham", "bacon", "pineapple"]

class MainFrame(Frame):
    def Body(self):
        p = FlexGridPanel(self, rows=10, cols=5, hgap=2, vgap=2)

        self.AddLabel(p, 1, 1, "First name:")
        self.AddLabel(p, 1, 2, "Last name:")
        self.AddLabel(p, 1, 3, "Phone:")
        self.AddLabel(p, 1, 4, "\nType of crust:", align='tr')
        self.AddLabel(p, 1, 5, "Toppings:", align='tr')
        self.AddLabel(p, 1, 6, "Super fast delivery ($2 extra):")

        # add controls
        p.AddComponent(3, 1, TextBox(p))
        p.AddComponent(3, 2, TextBox(p))
        p.AddComponent(3, 3, TextBox(p))
        p.AddComponent(3, 4, self.MakeCrustGroupBox(p))
        p.AddComponent(3, 5, self.MakeToppingsCheckListBox(p))
        p.AddComponent(3, 6, CheckBox(p))
        p.AddComponent(1, 8, self.MakeFakeButton(p), expand=0)

        p.Pack()
        self.AddComponent(p, expand='both', border=3)

        self.Pack()

        # fix weird colors on Windows
        self.BackgroundColor = p.BackgroundColor

    def AddLabel(self, parent, col, row, text, align=None):
        label = Label(parent, text)
        parent.AddComponent(col, row, label, expand=0, align=align or 'vr')
        # note: expand=0 allows us to align the label properly.
        # in this case, 'v' centers it vertically, and 'r' aligns it to
        # the right.

    def MakeCrustGroupBox(self, parent):
        g = GroupBox(parent, direction='v')
        for crust in CRUSTS:
            rb = RadioButton(g, " " + crust)
            g.AddComponent(rb, border=1)
        g.Pack()

        # check one by default
        g.Children[1].Value = True

        return g

    def MakeToppingsCheckListBox(self, parent):
        clb = CheckListBox(parent, choices=TOPPINGS, SizeY=100)
        return clb

    def MakeFakeButton(self, parent):
        b = Button(parent, "Order it already!")
        b.OnClick = lambda s: ShowMessage("Pay up", "Charging your credit card...")
        return b


app = Application(MainFrame, title='Order Form')
app.Run()

