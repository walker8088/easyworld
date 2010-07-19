# menudemo.py

import sys
sys.path.append("../..")
from wax import *

class MyFrame(Frame):

    def Body(self):
        self.SetSize((400, 200))
        self.CenterOnScreen()
        self.SetTitle("Playing with menus")

        self.CreateStatusBar()
        self.SetStatusText("This is the statusbar")

        tc = TextBox(self, text="""
A bunch of bogus menus have been created for this frame.  You
can play around with them to see how they behave and then
check the source for this sample to see how to implement them.
        """, readonly=1, multiline=1)
        self.AddComponent(tc)

        menubar = MenuBar(self)

        menu1 = Menu(self)
        menu1.Append("&Mercury", self.Menu101, "This the text in the statusbar")
        menu1.Append("&Venus", self.Menu102)
        menu1.Append("&Earth", self.Menu103, "You may select Earth too")
        menu1.AppendSeparator()
        menu1.Append("&Close", self.CloseWindow, "Close this frame")
        menubar.Append(menu1, "&Planets")

        menu2 = Menu(self)
        menu2.Append("Hydrogen", self.Menu201)
        menu2.Append("Helium", self.Menu202)
        # a submenu in the 2nd menu
        submenu = Menu(self)
        submenu.Append("Lanthanium", self.Menu2031)
        submenu.Append("Cerium", self.Menu2032)
        submenu.Append("Praesodymium", self.Menu2033)
        menu2.AppendMenu("Lanthanides", submenu)
        menubar.Append(menu2, "&Elements")

        menu3 = Menu(self)
        menu3.Append("IDLE", tooltip="a Python shell using tcl/tk as GUI",
         type='radio')
        menu3.Append("PyCrust", tooltip="a Python shell using wxPython as GUI",
         type='radio')
        menu3.Append("psi", tooltip="a simple Python shell using wxPython as GUI",
         type='radio')
        menu3.AppendSeparator()
        menu3.Append("project1")
        menu3.Append("project2")
        menubar.Append(menu3, "&Shells")

        menu4 = Menu(self)
        menu4.Append("letters", tooltip="abcde...", type='check')
        menu4.Append("digits", tooltip="123...", type='check')
        menu4.Append("letters and digits", tooltip="abcd... + 123...", type='check')
        menubar.Append(menu4, "Chec&k")

        menu5 = Menu(self)
        menu5.Append("Interesting thing", self.Foo, tooltip="Note the shortcut!",
         hotkey="Ctrl-A")
        menu5.AppendSeparator()
        menu5.Append("Hello", self.Hello, hotkey="Shift-H")
        #menu5.Append("With an icon", icon="moon16.gif")
        menubar.Append(menu5, "&Fun")

    def Menu101(self, event): print "Welcome to Mercury"
    def Menu102(self, event): print "Welcome to Venus"
    def Menu103(self, event): print "Welcome to the Earth"
    def CloseWindow(self, event): self.Close()
    def Menu201(self, event): print "Chemical element number 1"
    def Menu202(self, event): print "Chemical element number 2"
    def Menu2031(self, event): print "Chemical element number 57"
    def Menu2032(self, event): print "Chemical element number 58"
    def Menu2033(self, event): print "Chemical element number 59"
    def Foo(self, event): print "Foo!"
    def Hello(self, event): print "Hello!"

app = Application(MyFrame)
app.MainLoop()


