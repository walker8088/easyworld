#---------------------------------------------------------------------
# systemsettings.py
#   Allows one to fetch system settings
#   TODO:
#      - Make GetFont return a wax.Font
#      - GetScreenType returns should be parsed and made independent
#          from wx
#---------------------------------------------------------------------

import wx


cdata = {
    'scrollbar': wx.SYS_COLOUR_SCROLLBAR,
    'background': wx.SYS_COLOUR_BACKGROUND,
    'active_caption': wx.SYS_COLOUR_ACTIVECAPTION,
    'inactive_caption': wx.SYS_COLOUR_INACTIVECAPTION,
    'menu': wx.SYS_COLOUR_MENU,
    'window': wx.SYS_COLOUR_WINDOW,
    'window_frame': wx.SYS_COLOUR_WINDOWFRAME,
    'menu_text': wx.SYS_COLOUR_MENUTEXT,
    'window_text': wx.SYS_COLOUR_WINDOWTEXT,
    'caption_text': wx.SYS_COLOUR_CAPTIONTEXT,
    'active_boreder': wx.SYS_COLOUR_ACTIVEBORDER,
    'inactive_border': wx.SYS_COLOUR_INACTIVEBORDER,
    'app_workspace': wx.SYS_COLOUR_APPWORKSPACE,
    'highlight': wx.SYS_COLOUR_HIGHLIGHT,
    'highlight_text': wx.SYS_COLOUR_HIGHLIGHTTEXT,
    'button_face': wx.SYS_COLOUR_BTNFACE,
    'button_shadow': wx.SYS_COLOUR_BTNSHADOW,
    'gray_text': wx.SYS_COLOUR_GRAYTEXT,
    'button_text': wx.SYS_COLOUR_BTNTEXT,
    'inactive_caption_text': wx.SYS_COLOUR_INACTIVECAPTIONTEXT,
    'button_highlight': wx.SYS_COLOUR_BTNHIGHLIGHT,
    '3d_dark_shadow': wx.SYS_COLOUR_3DDKSHADOW,
    '3d_light': wx.SYS_COLOUR_3DLIGHT,
    'info_text': wx.SYS_COLOUR_INFOTEXT,
    'info_background': wx.SYS_COLOUR_INFOBK,
    'desktop': wx.SYS_COLOUR_DESKTOP,
    '3d_face': wx.SYS_COLOUR_3DFACE,
    '3d_shadow': wx.SYS_COLOUR_3DSHADOW,
    '3d_highlight': wx.SYS_COLOUR_3DHIGHLIGHT,
    '3d_hilight': wx.SYS_COLOUR_3DHILIGHT,
    '3d_button_hilight': wx.SYS_COLOUR_BTNHILIGHT,
}

fdata = {
    'oem_fixed': wx.SYS_OEM_FIXED_FONT,
    'ansi_fixed': wx.SYS_ANSI_FIXED_FONT,
    'ansi_var': wx.SYS_ANSI_VAR_FONT,
    'system': wx.SYS_SYSTEM_FONT,
    'device_default': wx.SYS_DEVICE_DEFAULT_FONT,
    'default_gui': wx.SYS_DEFAULT_GUI_FONT,
}

mdata = {
    'mouse_buttons': wx.SYS_MOUSE_BUTTONS,
    'border_x': wx.SYS_BORDER_X,
    'border_y': wx.SYS_BORDER_Y,
    'cursor_x': wx.SYS_CURSOR_X,
    'cursor_y': wx.SYS_CURSOR_Y,
    'dclick_x': wx.SYS_DCLICK_X,
    'dclick_y': wx.SYS_DCLICK_Y,
    'drag_x': wx.SYS_DRAG_X,
    'drag_y': wx.SYS_DRAG_Y,
    'edge_x': wx.SYS_EDGE_X,
    'edge_y': wx.SYS_EDGE_Y,
    'hscroll_arrow_x': wx.SYS_HSCROLL_ARROW_X,
    'hscroll_arrow_y': wx.SYS_HSCROLL_ARROW_Y,
    'hthumb_x': wx.SYS_HTHUMB_X,
    'icon_x': wx.SYS_ICON_X,
    'icon_y': wx.SYS_ICON_Y,
    'iconspacing_x': wx.SYS_ICONSPACING_X,
    'iconspacing_y': wx.SYS_ICONSPACING_Y,
    'windowmin_x': wx.SYS_WINDOWMIN_X,
    'windowmin_y': wx.SYS_WINDOWMIN_Y,
    'screen_x': wx.SYS_SCREEN_X,
    'screen_y': wx.SYS_SCREEN_Y,
    'framesize_x': wx.SYS_FRAMESIZE_X,
    'framesize_y': wx.SYS_FRAMESIZE_Y,
    'smallicon_x': wx.SYS_SMALLICON_X,
    'smallicon_y': wx.SYS_SMALLICON_Y,
    'hscroll_y': wx.SYS_HSCROLL_Y,
    'vscroll_x': wx.SYS_VSCROLL_X,
    'vscroll_arrow_x': wx.SYS_VSCROLL_ARROW_X,
    'vscroll_arrow_y': wx.SYS_VSCROLL_ARROW_Y,
    'vthumb_y': wx.SYS_VTHUMB_Y,
    'caption_y': wx.SYS_CAPTION_Y,
    'menu_y': wx.SYS_MENU_Y,
    'network_present': wx.SYS_NETWORK_PRESENT,
    'prewindows_present': wx.SYS_PENWINDOWS_PRESENT,
    'show_sounds': wx.SYS_SHOW_SOUNDS,
    'swap_buttons': wx.SYS_SWAP_BUTTONS,
}

sdata = {
    'none': wx.SYS_SCREEN_NONE,
    'tiny': wx.SYS_SCREEN_TINY,
    'pda': wx.SYS_SCREEN_PDA,
    'small': wx.SYS_SCREEN_SMALL,
    'desktop': wx.SYS_SCREEN_DESKTOP,
}


class _SystemSettings:
    def __init__(self):
        self.syscolordata = cdata
        self.sysfontdata = fdata
        self.sysmetricdata = mdata
        self.sysscreendata = sdata

    def GetColor(self, id):
        """ Find system color by id. """
        if isinstance(id, str):
            try:
                return wx.SystemSettings.GetColour(self.syscolordata[id])
            except KeyError:
                pass
            try:
                return wx.SystemSettings.GetColour(self.syscolordata[id.lower()])
            except KeyError:
                pass
        else:
            try:
                return wx.SystemSettings.GetColour(id)
            except KeyError:
                pass
        raise KeyError, id

    def GetColour(self, id):
        return self.GetColor(id)

    def GetColorList(self):
        return self.syscolordata.keys()

    def GetColourList(self):
        return self.syscolordata.keys()

    def GetFont(self, id):
        """ Find system font by id. """
        if isinstance(id, str):
            try:
                return wx.SystemSettings.GetFont(self.sysfontdata[id])
            except KeyError:
                pass
            try:
                return wx.SystemSettings.GetFont(self.sysfontdata[id.lower()])
            except KeyError:
                pass
        else:
            try:
                return wx.SystemSettings.GetFont(id)
            except KeyError:
                pass
        raise KeyError, id

    def GetFontList(self):
        return self.sysfontdata.keys()

    def GetMetric(self, id):
        """ Find system metric by id. """
        if isinstance(id, str):
            try:
                return wx.SystemSettings.GetMetric(self.sysmetricdata[id])
            except KeyError:
                pass
            try:
                return wx.SystemSettings.GetMetric(self.sysmetricdata[id.lower()])
            except KeyError:
                pass
        else:
            try:
                return wx.SystemSettings.GetMetric(id)
            except KeyError:
                pass
        raise KeyError, id

    def GetMetricList(self):
        return self.sysmetricdata.keys()

    def GetScreenType(self, id):
        """ Find screen type by id. """
        if isinstance(id, str):
            try:
                return wx.SystemSettings.GetScreenType(self.sysscreendata[id])
            except KeyError:
                pass
            try:
                return wx.SystemSettings.GetScreenType(self.sysscreendata[id.lower()])
            except KeyError:
                pass
        else:
            try:
                return wx.SystemSettings.GetScreenType(id)
            except KeyError:
                pass
        raise KeyError, id

    def GetScreenTypeList(self):
        return self.sysscreendata.keys()


SystemSettings = _SystemSettings()
