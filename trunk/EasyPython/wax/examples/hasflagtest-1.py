# hasflagtest.py


from wax import *
import wx


class MainFrame(Frame):
    def Body(self):
        tb = TextBox(self, justify='right', multiline=1, auto_url=1)
        print "Justification = ", repr(tb.HasStyle('justify'))
        print "Left Justification = " + repr(tb.HasStyle('justify', 'left'))
        print "Right Justification = " + repr(tb.HasStyle('justify', 'right'))
        print "Multiline = " + repr(tb.HasStyle('multiline'))
        print "Auto URL = " + repr(tb.HasStyle('auto_url'))
        print "asdf = " + repr(tb.HasStyle('asdf'))
        print "Rich = " + repr(tb.HasStyle('rich'))
        print "Rich2 = " + repr(tb.HasStyle('rich2'))
        print ""
        print "GetStyleDict: " + repr(tb.GetStyleDict())

if __name__ == "__main__":
    app = Application(MainFrame, title='test test...', direction='v')
    app.Run()
