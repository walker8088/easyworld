# filetreeview.py

import os
import string
import sys
import wx
from treeview import TreeView
from imagelist import ImageList

class FileTreeView(TreeView):

    def __init__(self, parent, rootdir="/"):
        TreeView.__init__(self, parent)
        self.rootdir = rootdir

        imagelist = ImageList(16, 16)
        imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16,16)), 'folder')
        imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16,16)), 'folder_open')
        self.SetImageList(imagelist)
        # XXX will need to be rewritten once Wax supports the ArtProvider

        self.MakeRoot()

    def SetImages(self, node):
        self.SetItemImage(node, self._imagelist['folder'], expanded=0)
        self.SetItemImage(node, self._imagelist['folder_open'], expanded=1)

    def MakeRoot(self):
        """ Add the toplevel nodes to the tree.  For Unix, this is simple:
            get the root directory, and look at the subdirectories there.
            For Windows, however, we have to get the available drive letters. """
        self.Clear()
        self.root = self.AddRoot(self.rootdir)
        self.SetImages(self.root)

        # get a list of tuples (short, long)
        if sys.platform == 'win32':
            a = self._win32_get_drive_letters()
            dirs = [(d, d) for d in a]
        else:
            dirs, files = self.GetDirectories(self.rootdir)

        self.AddDirs(self.root, dirs)
        self.Expand(self.root)

    def _win32_get_drive_letters(self):
        drives = []
        try:
            # check if win32all is available
            import win32api
        except ImportError:
            # if not, use os.path.exists to determine if drives exist
            # however, this may bring up an error dialog if there is no disk
            # in A:\
            for letter in string.uppercase:
                drive = letter + ":\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            drives = win32api.GetLogicalDriveStrings()
            drives = filter(None, string.splitfields(drives, "\000"))

        return drives

    def AddDirs(self, node, dirs):
        """ <dirs> is a list of tuples (short, long). """
        for short, long in dirs:
            child = self.AppendItem(node, short)
            self.SetPyData(child, long)
            self.SetImages(child)

    def GetDirectories(self, path):
        files = os.listdir(path)
        files = [(f, os.path.join(path, f)) for f in files]
        dirs = [(short, long) for (short, long) in files if os.path.isdir(long)]
        files = [(short, long) for (short, long) in files if not os.path.isdir(long)]
        return dirs, files

    def OnItemActivated(self, event):
        print dir(event), event.GetEventObject()

    def OnSelectionChanged(self, event):
        node = event.GetItem()
        if not self.HasChildren(node):
            path = self.GetPyData(node)
            dirs, files = self.GetDirectories(path)
            self.AddDirs(node, dirs)
            self.Expand(node)
            self.Refresh()
            self.ProcessFiles(dirs, files)

    def ProcessFiles(self, dirs, files):
        """ Do something with the dirs and files found.  Override this method
            in a subclass, or overwrite in an FileTreeView instance. """
        pass

