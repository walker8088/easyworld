# inject.py

import font

def inject(classes):
    """ Inject behavior into Wax classes. """
    for aclass in classes:

        # add a GetFont() that returns a Wax Font rather than a wxFont:
        def GetFont(self):
            wxfont = self._GetFont()
            wxfont.__class__ = font.Font
            return wxfont
        if hasattr(aclass, 'GetFont'):
            aclass._GetFont = aclass.GetFont
            aclass.GetFont = GetFont
