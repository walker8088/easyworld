# toolbar.py
# Contributed by Ivo van der Wijk.

from wax import waxobject, styles
import wx


"""
    API is more like wax.Menu API, not like wx.ToolBar API (i.e. Append
    in stead of Add*Tool

    No support for ToolRClicked or ToolEnter events (doesn't fit into api.
    The following API would be nicer:

    t = Tool(self.toolbar, "debug", "Enable debugging")
    ## alternative: CheckTool, RadioTool
    t.ToolClicked = self.start_debug
    t.toolRClicked = self.debug_options

    self.toolbar.AddComponent(t) # or Append

    However, there is no equivalent wx.Tool widget -- we'd have to define it
    from scratch.
"""

class ToolBar(wx.ToolBar, waxobject.WaxObject):

    __events__ = {
        'ToolClicked': wx.EVT_TOOL,
        'ToolRClicked': wx.EVT_TOOL_RCLICKED,
        'ToolEnter': wx.EVT_TOOL_ENTER,
    }

    def __init__(self, parent, **kwargs):
        style = 0
        style |= self.params(**kwargs)
        style |= styles.window(kwargs)

        self.id = wx.NewId()

        wx.ToolBar.__init__(self, parent, self.id, style=style)
        self.parent = parent
        self.BindEvents()

    def Append(self, title, bitmap, event=None, tooltip="", type="", hotkey=""):
        style = 0
        style |= {
            "r": wx.ITEM_RADIO,
            "c": wx.ITEM_CHECK,
        }.get(type.lower()[:1], wx.ITEM_NORMAL)

        id = wx.NewId()
        ## order for AddTool seems to be different from wx API?
        ## AddSimpleTool is somewhat undocumented
        item = self.AddSimpleTool(id, bitmap, title, tooltip, type)

        if event:
            wx.EVT_TOOL(self.parent, id, event)

        # else: do something like wax.Menu.handleAutoEvent

    def AppendSeparator(self):
        return self.AddSeparator()

    def _params(self, kwargs):
        flags = 0
        flags |= styles.stylebool('flat', wx.TB_FLAT, kwargs)
        flags |= styles.stylebool('dockable', wx.TB_DOCKABLE, kwargs)
        flags |= styles.stylebool('horizontal', wx.TB_HORIZONTAL, kwargs)
        flags |= styles.stylebool('vertical', wx.TB_VERTICAL, kwargs)
        flags |= styles.stylebool('text', wx.TB_TEXT, kwargs)
        flags |= styles.stylebool('noicons', wx.TB_NOICONS, kwargs)
        flags |= styles.stylebool('nodivider', wx.TB_NODIVIDER, kwargs)
        flags |= styles.stylebool('noalign', wx.TB_NOALIGN, kwargs)
        flags |= styles.stylebool('horz_layout', wx.TB_HORZ_LAYOUT, kwargs)
        flags |= styles.stylebool('horz_text', wx.TB_HORZ_TEXT, kwargs)
        return flags

