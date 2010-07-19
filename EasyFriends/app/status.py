from wx import *

import gob, irukaev, icons
from iruka_wdr import *

import gettext
_ = gettext.gettext

class JabberStatus(wx.Panel):
    '''Represent the status of user and detect idle'''
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # From wx.Designer
        StatusDlg( self )
        #self._statusBitmap = wx.PyTypeCast(self.FindWindowById(ID_STATUS_BITMAP), "wx.StaticBitmap")
        self._statusBitmap = self.FindWindowById(ID_STATUS_BITMAP)
	
        #self._statusCombo = wx.PyTypeCast(self.FindWindowById(ID_STATUS_COMBO), "wx.Choice")
        self._statusBitmap = self.FindWindowById(ID_STATUS_BITMAP)
	
        # Intialize variables
        self.__parent = self.GetParent()
        self.__status = 'offline'

        # Idle (auto-away)
        ID_MAIN_TIMER = wx.NewId()
        self.__mainTimer = wx.Timer(self, ID_MAIN_TIMER)
        self.__mainTimer.Start(1000) # Count every seconds...
        self.__elapsedTime = 0 # in seconds
        self.__goAwayTime = 600 # in seconds (now 10 minutes)
        self.__goXATime = 1200 # in seconds (now 20 minutes
        self.__leftFromIdle = False


        EVT_CHOICE(self.GetParent(), ID_STATUS_COMBO, self.onComboStatus)
        EVT_TIMER(self, ID_MAIN_TIMER, self.__CheckTime)
        EVT_MOUSE_EVENTS(self.GetParent(), self.__OnMouseMove)

    def GetStatus(self):
        return self.__status
        
    # Events
    def onComboStatus(self, event):
        newStatus = event.GetString()
        #self._statusCombo.SetStringSelection(self.__status)
        if (newStatus == 'online'):
            self.goOnline()
        elif (newStatus == 'offline'):
            self.goOffline()
        else:
            self.goOther(newStatus)

    # Interface with main window
    # (especially menu)

    def goOnline(self):
        '''Connect to server if offline, tell to server if we change status being connected.
        Do nothing if already connected.'''
        if self.__status == 'offline':
            self.__connectToServer()
            self.__status == 'connecting'
        elif self.__status in ['away', 'xa', 'dnd']:
            irukaglb.imcom.sendOnline()
            self.__changeStatusIndicators('online')
        self.__elapsedTime = 0

    def goOffline(self):
        '''Disconnect from server (if needed)'''
        if self.__status != 'offline':
            self.__disconnectFromServer()
        self.__changeStatusIndicators('offline')

    def goOther(self, newStatus, reason = ''):
        '''User wants to go away/na/busy. We tell it to server.'''
        if newStatus == "away":
            if reason == '':
                reason = self.__getReason("away", "I'm away.")
            irukaglb.imcom.sendAway(reason)
        if newStatus == "xa":
            if reason == '':
                reason = self.__getReason("xa", "I'm not available (away for a while).")
            irukaglb.imcom.sendXA(reason)
        if newStatus == "dnd":
            if reason == '':
                reason = self.__getReason("dnd", "I'm busy, please don't disturb me!")
            irukaglb.imcom.sendDND(reason)
        self.__changeStatusIndicators(newStatus)

    # GUI

    def __getReason(self, status, default):
        '''Show a dialog asking for a reason for new status'''
        dlg = wx.TextEntryDialog(self, _("Please explain why you will be") + " " + status, _("Going") + " " + status, default)
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return default


    def __changeStatusIndicators(self, status):
        '''Change information display about the status.'''
        # Change var
        self.__status = status
        # Change icon
        self._statusBitmap.SetBitmap(icons.bitmaps[status])
        if wx.Platform == '__WXMSW__':
            irukaglb.tbicon.SetIcon(icons.getwx.Icon(icons.bitmaps[status]), _(status))
        irukaglb.mainframe.SetIcon(icons.getwx.Icon(icons.bitmaps[status]))
        
        # Change combo
        self._statusCombo.SetStringSelection(status)

    # IMCOM Related functions
    
    def __connectToServer(self):
        '''Validate current profile and connect'''
        assert(self.__status == 'offline')
	irukaglb.imcom.changeProfile(
            irukaglb.profile.server, irukaglb.profile.port, irukaglb.profile.user,
            irukaglb.profile.password, irukaglb.profile.resource, 0,
            irukaglb.profile.priority, irukaglb.profile.encoding)
        irukaglb.imcom.connect()
        # PROBLEM: is in a thread so app is blocked. TODO: Change that in IMCOM.

    def __disconnectFromServer(self):
        '''User wants to disconnect'''
        if irukaglb.debug == 1:
            print "status: Disconnecting..."
        irukaglb.imcom.disconnect()

    def __onLoginAnswer(self, successful):
        """This function is called by the IMCom library. It lets us
	know whether the login was successful or not."""
	if(successful):
            self.__changeStatusIndicators('online')
	else:
            retry = wx.MessageBox(_("Error connecting to server! Retry?"), _("Connection error"),
                                 wx.YES_NO|wx.ICON_EXCLAMATION, self.GetParent());
            if retry:
                self.goOnline()

    def __onDisconnect(self):
        '''This function is called by IMCOM if we are brutally disconnected.'''
        self.__changeStatusIndicators('offline')

    # Timer

    def __CheckTime(self, event):
        if self.__status in ['online', 'away', 'xa']:
            self.__elapsedTime = self.__elapsedTime + 1
        if (self.__elapsedTime > self.__goXATime) and (self.__status in ['online', 'away']):
            self.goOther("xa", _("Extended away (due to idle)"))
            self.__leftFromIdle = True
        elif (self.__elapsedTime > self.__goAwayTime) and (self.__status in ['online']):
            self.goOther("away", _("Away (due to idle)"))
            self.__leftFromIdle = True

    def __OnMouseMove(self, event):
        self.__elapsedTime = 0
        if self.__leftFromIdle:
            self.goOnline()
            self.__leftFromIdle = False
            
