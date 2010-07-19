# choicedialog.py

from wax.dialog import Dialog
from wax.label import Label
from wax.listbox import ListBox

class ChoiceDialog(Dialog):
    """ Dialog to choose an item from a list.  The selected item can be
        retrieved through the .choice attribute. """

    def __init__(self, parent, title="Choice dialog", prompt="Choose one:",
                 choices=[], selection='single'):
        self.prompt = prompt
        self.choices = choices[:]
        self.selection = selection
        self.choice = -1  # this will be the index of the chosen item
        Dialog.__init__(self, parent, title)

    def Body(self):
        self.label = Label(self, self.prompt)
        self.AddComponent(self.label, stretch=1, border=7)

        self.chooser = ListBox(self, self.choices, size=(100,100),
                       selection=self.selection)
        self.AddComponent(self.chooser, stretch=1, expand=1, border=5)
        self.chooser.OnDoubleClick = self.OnListBoxDoubleClick

    def OnListBoxDoubleClick(self, event):
        # double-clicking in the list is the same as selecting an item and
        # pressing OK
        self.OnClickOKButton(event)

    def Validate(self):
        if self.selection == 'single':
            self.choice = self.chooser.GetSelection()
            if self.choice < 0:
                raise ValueError, "No item selected"
        else:
            self.choice = self.chooser.GetSelections()
            if self.choice == []:
                raise ValueError, "No item selected"
        # XXX not sure if this is how it's supposed to be... Validate()
        # should return 0, and "somehow" OnValidateError should do the error
        # message?
        return 1

    def GetSelection(self):
        return self.choice  # just an alias

