#---------------------------------------------------------------
# wizard.py
#    Author: Hans Nohawk
#    Update: Jason Gedge
#
# TODO:
#  - Add some mechanism for changing the bitmap
#---------------------------------------------------------------

from wax import Container, Line, Panel, VerticalPanel, OverlayPanel, Button, Bitmap, WaxObject
import wx

class Wizard(wx.Dialog, Container):
    def __init__(self, parent, title, bitmap=None):
        wx.Dialog.__init__(self, parent, wx.NewId(), title, wx.DefaultPosition)

        self._create_sizer('vertical')
        self.SetDefaultFont()
        self.bitmap = bitmap

        # enter stuff here...
        self.Body() 
        # does not need Pack(), we will do that here, after adding a few more
        # controls

        # add line and buttons pane...
        line = Line(self, size=(20,-1), direction='horizontal')
        panel = Panel(self, direction='horizontal')

        self.backbutton = Button(panel, "Back")
        self.backbutton.Disable()
        self.nextbutton = Button(panel, "Next")
        self.cancelbutton = Button(panel, "Cancel")

        panel.AddSeparator(20)
        panel.AddComponent(self.backbutton, expand=1, border=1)
        panel.AddComponent(self.nextbutton, expand=1, border=1)
        panel.AddComponent(self.cancelbutton, expand=1, border=1)
        panel.Pack()

        #wx.EVT_CHAR_HOOK(self, self.OnCharHook)

        self.AddComponent(line, align='center', stretch=1, border=5)
        self.AddComponent(panel, border=5, align='r')  # yay!
        self.Pack()
        self.Centre()

    def Body(self):
        p = Panel(self, direction='h')
        self.AddComponent(p)

        self.mainpanel = OverlayPanel(p)
        self.MakePages()

        if self.bitmap:
            bitmap = Bitmap(p, self.bitmap)
            p.AddComponent(bitmap, border=10)
        p.AddComponent(self.mainpanel, border=5, expand='b', stretch=1)
        p.Pack()

    def Run(self):
        """ Run the current wizard. """
        #self.MakePages()
        self.pages[0].UpdateEvents()

        try:
            self.mainpanel.Select(0)
        except IndexError:
            raise ValueError, "Wizard object has no pages"
        return self.ShowModal()

    def End(self):
        self.EndModal(wx.ID_CANCEL)

    def GetPages(self):
        """ Return a list of page classes. """
        return []

    def MakePages(self):
        """ Creates a list of wizard pages. """
        pagelist = self.GetPages()
        self.pages = []
        i = 0

        for pagefactory in pagelist:
            page = pagefactory(self, self.mainpanel)
            page.number = i
            self.AddPage(page)
            i += 1

        for i in range( len(self.pages) ):
            page = self.pages[i]
            if i == 0:
                page.prev = None
            else:
                page.prev = self.pages[i - 1]

            if i == len(self.pages) - 1:
                page.next = None
            else:
                page.next = self.pages[i + 1]

        self.mainpanel.Pack()

    def AddPage(self, page):
        """ Add a WizardPage instance. """
        self.pages.append(page)
        self.mainpanel.AddComponent(page, expand=1, stretch=1)

    def OnNewPage(self, old, new):
        """ [Event] Called whenever a new page is displayed.
            Note: This version assumes the last page in the list is
                  the last page, and changes next to finish appropriately.
                  Override this event if you don't want that! """

        if old.next and not new.next:
            self.nextbutton.SetLabel('Finish')
        elif not old.next and new.next:
            self.nextbutton.SetLabel('Next')

class WizardPage(VerticalPanel):
    def __init__(self, wizard, *args, **kwargs):
        # default values
        self.enablecancel = True
        self.enableback = True
        self.enablenext = True
        
        VerticalPanel.__init__(self, *args, **kwargs) # will call Body()
        self.wizard = wizard

    def OnPreviousPage(self, event=None):
        """ Override this if you want to control what happens when the Back
            Button is pressed. As it stands, it will go back one page. """
        if self.prev:
            self.wizard.mainpanel.SelectPrevious()
            self.prev.UpdateEvents()
            if not self.prev.prev:
                self.wizard.backbutton.Disable()
        self.wizard.OnNewPage(self, self.prev) #<----- Maybe have OverlayPanel relay Panel
                                               #       changed events to make this simpler?
    def OnNextPage(self, event=None):
        """ Override this if you want to control what happens when the Next/Finish
            Button is pressed. As it stands, it will go ahead one page or end the
            wizard, depending on the state of the button. """
        if self.next:
            self.wizard.mainpanel.SelectNext()
            self.wizard.backbutton.Enable()
            self.next.UpdateEvents()
            self.wizard.OnNewPage(self, self.next)
        else:
            self.wizard.End()

    def ChangePage(self):
        """ Switch to the page that was defined by self.SetTarget(). """
        self.wizard.mainpanel.Select(self.target)
        self._EnableButtons()
        page = self.wizard.pages[self.target]
        page.UpdateEvents()
        self.wizard.OnNewPage(self, page)

    def _EnableButtons(self):
        """ Enables/Disables the buttons based on current settings. """
        if self.enableback:
            self.wizard.backbutton.Enable()
        else:
            self.wizard.backbutton.Disable()

        if self.enablenext:
            self.wizard.nextbutton.Enable()
        else:
            self.wizard.nextbutton.Disable()

        if self.enablecancel:
            self.wizard.cancelbutton.Enable()
        else:
            self.wizard.cancelbutton.Disable()

    def OnCancel(self, event=None):
        self.wizard.End()

    def SetTarget(self, target, enableback=True, enablenext=True, enablecancel=True):
        """ Sets the target page for self.ChangePage(). """
        self.target = target
        self.enableback = enableback
        self.enablenext = enablenext
        self.enablecancel = enablecancel

    def UpdateEvents(self):
        """ Changes the events associated with the buttons on the wizard. """
        self.wizard.backbutton.OnClick = self.OnPreviousPage
        self.wizard.nextbutton.OnClick = self.OnNextPage
        self.wizard.cancelbutton.OnClick = self.OnCancel
