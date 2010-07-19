
__doc__ = """
Iruka's event subsystem.

To register an event handler, use register_handler() function.  To
unregister an event handler use unregister_handler() function.

To switch the 'on' button for event subsystem call
register_callbacks() function.

To execute all handlers for some event user fire_event().
"""

import wx 
import threading

import glob

IM_CONNECTED_EVENT = wx.NewEventType()
EVT_IM_CONNECTED = wx.PyEventBinder(IM_CONNECTED_EVENT, 1)  

IM_DISCONNECTED_EVENT = wx.NewEventType()
EVT_IM_DISONNECTED = wx.PyEventBinder(IM_DISCONNECTED_EVENT, 1)  

IM_PRESENCE_UPDATE_EVENT = wx.NewEventType()
EVT_IM_PRESENCE_UPDATE = wx.PyEventBinder(IM_PRESENCE_UPDATE_EVENT, 1)  

IM_ROSTER_UPDATE_EVENT = wx.NewEventType()
EVT_IM_ROSTER_UPDATE = wx.PyEventBinder(IM_ROSTER_UPDATE_EVENT, 1)  

class ImEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.msg = None

    def SetMessage(self, msg):
        self.msg = msg

    def GetMessage(self):
        return self.msg

class ImEventHandler:
    def bindTo(self, connection):
        self._connection = connection
        
        connection.cbHandleConnected = self.cbHandleConnected
        connection.cbHandleDisconnected = self.cbHandleDisconnected
        connection.cbHandlePresenceUpdate = self.cbHandlePresenceUpdate
        connection.cbHandleMessageReceive = self.cbHandleMessageReceive        
        connection.cbHandleSubscribed = self.cbHandleSubscribed
        connection.cbHandleUnsubscribed = self.cbHandleUnsubscribed
        connection.cbHandleRosterUpdate = self.cbHandleRosterUpdate
    
    def cbHandleConnected(self) :
        print "cbHandleConnected"
        evt = ImEvent(EVT_IM_CONNECTED, -1)
        self.GetEventHandler().ProcessEvent(evt)
        
    def cbHandleDisconnected(self) :
        print "disconnected"
        evt = ImEvent(EVT_IM_DISCONNECTED, -1)
        self.GetEventHandler().ProcessEvent(evt)
       
    def cbHandlePresenceUpdate(self, msg) :
        evt = ImEvent(EVT_IM_PRESENCE_UPDATE, -1)
        self.GetEventHandler().ProcessEvent(evt)
       
    def cbHandleMessageReceive(self, msg) :
        pass
       
    def cbHandleSubscribed(self, msg) :
        pass
        
    def cbHandleUnsubscribed(self) :
        pass
        
    def cbHandleRosterUpdate(self) :
        print "onRosterUpdated"
        evt = ImEvent(EVT_IM_ROSTER_UPDATE, -1)
        self.GetEventHandler().ProcessEvent(evt)
    
events = {
    'Connected': [],
    'Disconnected': [],
    'PresenceUpdate': [],
    'MessageReceive': [],
    'Subscribed': [],
    'Unsubscribed': [],
    'RosterUpdate': [],
    'ApplicationExit': []
    }

IM_APP_EVENT = wx.NewId()
event_handled = threading.Event()

class AppEvent(wx.PyEvent):
    "An Iruka event."
    def __init__(self, event, *args, **kwargs):
        wxPyEvent.__init__(self)
        self.SetEventType(IM_APP_EVENT)
        self.args = (event,) + args
        self.kwargs = kwargs

def register_handler(event, handler):
    """
    Register a new 'handler' function for an 'event', which is one of
    irukaev.events.keys().
    """
    if not (event in events.keys()):
        raise ArgumentError("Unknown event '%s'" % str(event))
    events[event].append(handler)

def unregister_handler(event, handler):
    """
    Removes 'handler' from list of handlers for an 'event'.
    """
    events[event].remove(handler)

def _run_handlers(event, *args, **kwargs):
    """
    [PRIVATE] Run handlers for an event and signalise imclient-thread
    that this event is handled.
    """
    fire_event(event, *args, **kwargs)
    event_handled.set()

def fire_event(event, *args, **kwargs):
    """
    Fire and handle 'event'.
    """
    print "fire_event here"
    for h in events[event]:
        if apply(h, args, kwargs):
            break

def on_jabber_event(e):
    print "on_jabber_event"
    apply(_run_handlers, e.args, e.kwargs)

def cbHandleXXX(listener, event, *args, **kwargs):
    """
    This is generic callback for Jabber events.
    """
    print "Event: " + event
    event_handled.clear()
    wxPostEvent(listener, AppEvent(event, *args, **kwargs))
    event_handled.wait()

def register_callbacks(listener):
    """
    Init event system.  'listener' should be an instance of
    wxEvtHandler.  It will be used as a dispatcher for messages.
    Recommended value for it is application's main window.
    """
    listener.Bind(IM_APP_EVENT, on_jabber_event)

    glob.imclient.cbHandleConnected = lambda *a, **k: cbHandleXXX(listener, 'Connected', *a, **k)
    glob.imclient.cbHandleDisconnected = lambda *a, **k: cbHandleXXX(listener, 'Disconnected', *a, **k)
    glob.imclient.cbHandlePresenceUpdate = lambda *a, **k: cbHandleXXX(listener, 'PresenceUpdate', *a, **k)
    glob.imclient.cbHandleMessageReceive = lambda *a, **k: cbHandleXXX(listener, 'MessageReceive', *a, **k)
    glob.imclient.cbHandleSubscribed = lambda *a, **k: cbHandleXXX(listener, 'Subscribed', *a, **k)
    glob.imclient.cbHandleUnsubscribed = lambda *a, **k: cbHandleXXX(listener, 'Unsubscribed', *a, **k)
    glob.imclient.cbHandleRosterUpdate = lambda *a, **k: cbHandleXXX(listener, 'RosterUpdate', *a, **k)
    