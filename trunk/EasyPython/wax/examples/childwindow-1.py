# childwindow-1.py
# Not really a "child" window, but a window that is controlled by the
# main one...

from wax import *

class ChildWindow(Frame):
    def Body(self):
        label = Label(self, "I am a happy child window!")
        self.AddComponent(label, border=30)
        self.Pack()

class MainFrame(VerticalFrame):

    def Body(self):
        # create and hide child window
        self.childwindow = ChildWindow(self, minimize_box=0, maximize_box=0,
                           close_box=0) # disable buttons
        self.childwindow.Hide()

        showbutton = Button(self, "Show child window", event=self.ShowChildWindow)
        self.AddComponent(showbutton, border=5)
        hidebutton = Button(self, "Hide child window", event=self.HideChildWindow)
        self.AddComponent(hidebutton, border=5)

        self.Pack()

    def ShowChildWindow(self, event):
        self.childwindow.Show()
        # or: ShowModal(), but this window doesn't have a way to exit
        # also see: stay_on_top flag

    def HideChildWindow(self, event):
        self.childwindow.Hide()

app = Application(MainFrame, title='childwindow-1')
app.Run()
