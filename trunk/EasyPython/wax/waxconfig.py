# waxconfig.py

import font

class WaxConfig:
    def __init__(self):
        self.default_font = ("Tahoma", 8)
        # the default font that is used for all widgets that support it.
        # note that we can't create an instance of Font, because wxPython
        # doesn't allow instantiation before an Application has been created.

        self.check_parent = False
        # when True: when we add a widget to a container, check if that
        # widget's parent is the same as that container; if not, display
        # a warning

WaxConfig = WaxConfig()
