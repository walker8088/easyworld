# core-getapp.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        app = core.GetApp()
        print app
        assert isinstance(app, Application)

app = Application(MainFrame, title="core-getapp")
app.Run()

