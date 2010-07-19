
class PluginManager :
    EVT_DRPY_DOCUMENT_CHANGED,\
    EVT_DRPY_FILE_OPENING, EVT_DRPY_FILE_OPENED,\
    EVT_DRPY_FILE_SAVING,  EVT_DRPY_FILE_SAVED,\
    EVT_DRPY_FILE_CLOSING, EVT_DRPY_FILE_CLOSED,\
    EVT_DRPY_NEW = range(8)
    
    def __init__(self, frame) :
        self.frame = frame
        self.drpyevents = []
 
    def PBind(self, eventtype, function, *args):
        self.drpyevents.append((eventtype, function, args))

    def PPost(self, eventtype):
        for evt in self.drpyevents:
            if evt[0] == eventtype:
                if evt[2]:
                    apply(evt[1], evt[2])
                else:
                    evt[1]()
                    
    def PUnbind(self, eventtype, function):
        x = 0
        for evt in self.drpyevents:
            if (evt[0] == eventtype) and (evt[1] == function):
                self.drpyevents.pop(x)
            else:
                x += 1
       