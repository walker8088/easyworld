# overlaypanel.py

# todo: styles

from containers import OverlayContainer
import wx

class OverlayPanel(wx.Panel, OverlayContainer):
    def __init__(self, parent=None):
        wx.Panel.__init__(self, parent or None, wx.NewId())

        self.current_win = -1
        self._create_sizer()
        self.SetDefaultFont()
        self.Body()

    def Select(self, n):
        if n != self.current_win and n < len(self.windows) and n >= 0:
            for window in self.windows:
                window.Hide()
            self.windows[n].Show()
            self.current_win = n

    def SelectRelative(self, n):
        new = self.current_win + n
        if n != 0 and new < len(self.windows) and new >= 0:
            self.windows[self.current_win].Hide()
            self.current_win = new
            self.windows[self.current_win].Show()

    def SelectNext(self):
        if self.current_win + 1 < len(self.windows):
            self.windows[self.current_win].Hide()
            self.current_win = self.current_win + 1
            self.windows[self.current_win].Show()

    def SelectPrevious(self):
        if self.current_win >= 0:
            self.windows[self.current_win].Hide()
            self.current_win = self.current_win - 1
            self.windows[self.current_win].Show()
