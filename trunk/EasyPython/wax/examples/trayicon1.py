# trayicon1.py
# Based on wxPython example at http://norfolkgraphics.com/python.php

from wax import *

class MainFrame(Frame):

    def Body(self):
        self.tbicon = TaskBarIcon()
        self.status = 0
        self.UpdateIcon()

        self.tbicon.OnLeftDoubleClick = self.RestoreWindow
        self.tbicon.OnRightUp = self.ShowTaskBarMenu

        self.Show(1)

    def UpdateIcon(self):
        """ Update icon based on current state. """
        if self.status == 0:
            self.tbicon.SetIcon('icon1.ico', 'Icon demo - state 1')
        else:
            self.tbicon.SetIcon('icon2.ico', 'Icon demo - state 2')

    def ToggleIcon(self, event):
        self.status = not self.status
        self.UpdateIcon()

    def RestoreWindow(self, event=None):
        """ Show/restore main window. """
        self.Show(1)
        self.Iconize(0)

    def HideWindow(self, event=None):
        self.Iconize(1)

    def ShowTaskBarMenu(self, event=None):
        menu = Menu(self.tbicon)

        # choose Show/Hide based on current window state
        if self.IsIconized():
            menu.Append('&Show window', self.RestoreWindow)
        else:
            menu.Append('&Hide window', self.HideWindow)

        # these entries are always present
        menu.Append('&Toggle Icon', self.ToggleIcon)
        menu.Append('E&xit', self.ExitApp)

        self.tbicon.PopupMenu(menu)
        #menu.Destroy()  # ...why?
        #core.wx.GetApp().ProcessIdle()   # ...?

    def ExitApp(self, event):
        self.Close()

    def OnIconize(self, event=None):
        self.Iconize(1) # minimize
        self.Show(0)    # hide taskbar button

    def OnClose(self, event):
        # unfortunately, this is necessary, otherwise the program will hang
        # on exit
        self.tbicon.Destroy()
        event.Skip()


if __name__ == "__main__":

    app = Application(MainFrame, title='trayicon demo')
    app.Run()

