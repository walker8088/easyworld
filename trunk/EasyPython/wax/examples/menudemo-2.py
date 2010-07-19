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
        menu1.Append("&Mercury", tooltip="This the text in the statusbar")
        menu1.Append("&Venus")
        menu1.Append("&Earth", tooltip="You may select Earth too")
        menu1.AppendSeparator()
        menu1.Append("&Close", tooltip="Close this frame")
        menubar.Append(menu1, "&Planets")

        menu2 = Menu(self)
        menu2.Append("Hydrogen")
        menu2.Append("Helium")
        # a submenu in the 2nd menu
        submenu = Menu(self)
        submenu.Append("Lanthanium")
        submenu.Append("Cerium")
        submenu.Append("Praesodymium")
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
        menu5.Append("Interesting thing", tooltip="Note the shortcut!",
         hotkey="Ctrl-A")
        menu5.AppendSeparator()
        menu5.Append("Hello", self.Hello, hotkey="Shift-H")
        #menu5.Append("With an icon", icon="moon16.gif")
        menubar.Append(menu5, "&Fun")

        # demonstrate menubar.Walk()
        for mwitem in menubar.Walk():
            print mwitem.name, [(item.GetLabel(), item.GetId())
                                for item in mwitem.items]

    def Menu_Planets_Mercury(self, event): print "Welcome to Mercury"
    def Menu_Planets_Venus(self, event): print "Welcome to Venus"
    def Menu_Planets_Earth(self, event): print "Welcome to the Earth"
    def Menu_Planets_Close(self, event): self.Close()
    def Menu_Elements_Hydrogen(self, event):
        print "Chemical element number 1"
    def Menu_Elements_Helium(self, event):
        print "Chemical element number 2"
    def Menu_Elements_Lanthanides_Lanthanium(self, event):
        print "Chemical element number 57"
    def Menu_Elements_Lanthanides_Cerium(self, event):
        print "Chemical element number 58"
    def Menu_Elements_Lanthanides_Praesodymium(self, event):
        print "Chemical element number 59"
    def Menu_Fun_Interesting_thing(self, event): print "Foo!"
    def Hello(self, event): print "Hello!"

app = Application(MyFrame)
app.MainLoop()


