# image.py

import wx
import waxobject

_handlers = {}

def AddImageHandler(type):
    d = {
        "bmp": wx.BMPHandler,
        "png": wx.PNGHandler,
        "jpg": wx.JPEGHandler,
        "gif": wx.GIFHandler,
        "pcx": wx.PCXHandler,
        "pnm": wx.PNMHandler,
        "tiff": wx.TIFFHandler,
        #"iff": wx.IFFHandler,
        #"xpm": wx.XPMHandler,
        "ico": wx.ICOHandler,
        "cur": wx.CURHandler,
        "ani": wx.ANIHandler,
    }
    key = type.lower()
    handler = d[key]
    wx.Image_AddHandler(handler())
    _handlers[key] = 1

def AddAllImageHandlers():
    wx.InitAllImageHandlers()

class Image(wx.Image, waxobject.WaxObject):

    def __init__(self, filename, type=None, autoinstall=1):
        lfilename = filename.lower()
        t = 0

        # if type isn't set, try to grok it from the filename.
        if not type:
            if lfilename.endswith(".bmp"):
                type = 'bmp'
            elif lfilename.endswith(".gif"):
                type = 'gif'
            elif lfilename.endswith(".png"):
                type = 'png'
            elif lfilename.endswith(".jpg") or lfilename.endswith(".jpeg"):
                type = 'jpg'
            elif lfilename.endswith(".pcx"):
                type = 'pcx'
            elif lfilename.endswith(".ico"):
                type = 'ico'

        t = {
            "bmp": wx.BITMAP_TYPE_BMP,
            "gif": wx.BITMAP_TYPE_GIF,
            "png": wx.BITMAP_TYPE_PNG,
            "jpg": wx.BITMAP_TYPE_JPEG,
            "jpeg": wx.BITMAP_TYPE_JPEG,
            "pcx": wx.BITMAP_TYPE_PCX,
            "ico": wx.BITMAP_TYPE_ICO,
        }.get(type.lower(), 0)

        if not t:
            raise ValueError, "Could not determine bitmap type of '%s'" % (
                  filename,)

        # if autoinstall is true, install handler on demand
        if autoinstall:
            if not _handlers.has_key(type):
                AddImageHandler(type)

        wx.Image.__init__(self, filename, t)


def ImageAsBitmap(filename, *args, **kwargs):
    return Image(filename, *args, **kwargs).ConvertToBitmap()

