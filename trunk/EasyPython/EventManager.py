
import wx
import wx.lib.newevent

FileNewEvent,\
EVT_FILE_NEW = wx.lib.newevent.NewCommandEvent() 

FileLoadingEvent,\
EVT_FILE_OPENING = wx.lib.newevent.NewCommandEvent()

FileLoadedEvent,\
EVT_FILE_OPENED = wx.lib.newevent.NewCommandEvent()

FileSavingEvent,\
EVT_FILE_SAVING = wx.lib.newevent.NewCommandEvent()

FileSavedEvent,\
EVT_FILE_SAVED = wx.lib.newevent.NewCommandEvent()

FileClosingEvent,\
EVT_FILE_CLOSING = wx.lib.newevent.NewCommandEvent()

FileClosedEvent,\
EVT_FILE_CLOSED = wx.lib.newevent.NewCommandEvent()  

FileChangedEvent,\
EVT_FILE_CHANGED = wx.lib.newevent.NewCommandEvent()

SelectChangedEvent,\
EVT_SELECT_CHANGED = wx.lib.newevent.NewCommandEvent()
   
class EventManager(wx.EvtHandler) : 
    def __init__(self, frame) :
        
        wx.EvtHandler.__init__(self)
        
        self.frame = frame
        
    def PostFileNewEvent(self, doc) :
        event = FileNewEvent(-1, doc = doc)
        self.ProcessEvent(event)
         
    def PostFileLoadingEvent(self, doc) :
        event = FileLoadingEvent(-1, doc = doc)
        self.ProcessEvent(event)
        
    def PostFileLoadedEvent(self, doc) :
        event = FileLoadedEvent(-1, doc = doc)
        self.ProcessEvent(event)
        
    def PostFileChangedEvent(self, doc) :
        event = FileChangedEvent(-1, doc = doc)
        self.ProcessEvent(event)
        
    def PostFileSavingEvent(self, doc) :
        event = FileSavingEvent(-1, doc = doc)
        self.ProcessEvent(event)
        
    def PostFileSavedEvent(self, doc) :
        event = FileSavedEvent(-1, doc = doc)
        self.ProcessEvent(event)
    
    def PostFileClosingEvent(self, doc) :
        event = FileClosingEvent(-1, doc = doc)
        self.ProcessEvent(event)
        
    def PostFileClosedEvent(self, doc) :
        event = FileClosedEvent(-1, doc = doc)
        self.ProcessEvent(event)
        
    def PostSelectChangedEvent(self, doc, index) :
        event = SelectChangedEvent(-1, doc = doc, index = index)
        self.ProcessEvent(event)
        