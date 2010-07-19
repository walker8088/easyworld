# errordialog.py

from wax import Dialog, Font, Label, TextBox
#
import cStringIO
import pprint
import traceback

FIXED_FONT_SMALLER = ("Courier New", 9)

class ErrorDialog(Dialog):

    def __init__(self, parent, exctype, excvalue, traceback):
        self.exctype = exctype
        self.excvalue = excvalue
        self.traceback = traceback
        self.FIXED_FONT_SMALLER = Font("Courier New", 9)
        Dialog.__init__(self, parent, "An error occurred", cancel_button=0)

    def Body(self):
        label = Label(self, "An unexpected error occurred.\n"
         "Please notify the author of the program, preferably with a copy "
         "of the full traceback listed below.")
        self.AddComponent(label, stretch=1, border=7)

        text = TextBox(self, size=(550,210), multiline=1, wrap=0, readonly=1)
        text.SetFont(self.FIXED_FONT_SMALLER)
        c = cStringIO.StringIO()
        traceback.print_exception(self.exctype, self.excvalue, self.traceback,
         file=c)
        text.AppendText(c.getvalue())

        # if the exception object has an attribute named 'globals', display its
        # contents, except for __builtins__
        if hasattr(self.excvalue, 'globals'):
            text.AppendText('\nglobals:\n')
            del self.excvalue.globals["__builtins__"]
            c2 = cStringIO.StringIO()
            pprint.pprint(self.excvalue.globals, c2)
            text.AppendText(c2.getvalue())

        self.AddComponent(text, expand=1, stretch=1, border=5)

        text.SetFocus()

# The 'get error information' stuff looks generic and should probably be
# refactored out.
