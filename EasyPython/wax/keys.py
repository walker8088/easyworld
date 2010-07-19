# keys.py

from wx import *

class keys:
    enter = WXK_RETURN
    # 'return' is not valid; reserved word

    alt = WXK_ALT
    control = ctrl = WXK_CONTROL
    shift = WXK_SHIFT

    f1 = F1 = WXK_F1
    f2 = F2 = WXK_F2
    f3 = F3 = WXK_F3
    f4 = F4 = WXK_F4
    f5 = F5 = WXK_F5
    f6 = F6 = WXK_F6
    f7 = F7 = WXK_F7
    f8 = F8 = WXK_F8
    f9 = F9 = WXK_F9
    f10 = F10 = WXK_F10
    f11 = F11 = WXK_F11
    f12 = F12 = WXK_F12

    insert = WXK_INSERT
    delete = WXK_DELETE
    home = WXK_HOME
    end = WXK_END

    up = cursor_up = WXK_UP
    down = cursor_down = WXK_DOWN
    left = cursor_left = WXK_LEFT
    right = cursor_right = WXK_RIGHT

    pageup = pgup = WXK_PRIOR   # not: WXK_PAGEUP
    pagedown = pgdown = pgdn = WXK_NEXT # not: WXK_PAGEDOWN

    tab = WXK_TAB
    backspace = bsp = WXK_BACK
    esc = escape = WXK_ESCAPE

    # XXX more later...?

