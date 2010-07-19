# maskedtextbox-1.py
# NOTE: Currently unsupported!

from wax import *

FONT = ("Courier New", 10)

class MainFrame(Frame):
    def Body(self):
        controls = [
            ("(###) ###-#### x:###", "^\(\d{3}\) \d{3}-\d{4}"), # phone number
            ("\FA\HRA\NHAA\T 9/11", "F[A-Z]HR[A-Z]NH[A-Z][A-Z]T 9/11"), # wheel of fortune word
            # this format is retarded... sigh!!
            # try to make it match the word "AND"...
        ]
        for data in controls:
            ed = MaskedTextBox(self, mask=data[0], validRegex=data[1], formatcodes="F!")
            ed.SizeX = 160
            ed.Font = FONT
            self.AddComponent(ed, stretch=1)
        self.Pack()

app = Application(MainFrame, direction='v')
app.Run()
