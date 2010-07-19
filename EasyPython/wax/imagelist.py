"""\
imagelist.py

Wax's version of the wxImageList is a bit more user-friendly:

Rather than forcing you to keep the indexes around or know them by heart,
you can (optionally) add names for the images you add, then look them up to
retrieve the index:

  imagelist.Add(bitmap, 'folder')
  imagelist.Add(bitmap, 'folder_open')

  somecontrol.SetItemImage(node, imagelist['folder'])

"""

import wx

class ImageList(wx.ImageList):

    def __init__(self, *args, **kwargs):
        wx.ImageList.__init__(self, *args, **kwargs)
        self._names = {}

    def Add(self, bitmap, name=None):
        index = wx.ImageList.Add(self, bitmap)
        if name:
            self._names[name] = index
        return index

    def GetIndexByName(self, name):
        return self._names[name]

    def __getitem__(self, name):
        return self.GetIndexByName(name)
