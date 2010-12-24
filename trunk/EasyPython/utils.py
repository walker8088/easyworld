#coding:utf-8
import os
import sys
import re
import wx
import config, EpyGlob

def GetFileExt(index):
        thelist = config.prefs.extensions[index].split(',')
        thestring = ''
        for t in thelist:
            thestring += '(\.' + t.strip() + '$)|'

        return thestring[:-1]
        
global refiletypeispy,refiletypeishtml,refiletypeistxt

def Init() :
    global refiletypeispy,refiletypeishtml,refiletypeistxt
    refiletypeispy = re.compile(GetFileExt(0), re.IGNORECASE)
    refiletypeishtml = re.compile(GetFileExt(1), re.IGNORECASE)
    refiletypeistxt = re.compile(GetFileExt(2), re.IGNORECASE)
        
def IsHtmlFile(filename):
        return refiletypeishtml.search(filename) is not None

def IsPlainTextFile(filename):
        return refiletypeistxt.search(filename) is not None

def IsPythonFile(filename):
        return refiletypeispy.search(filename) is not None

import drScrolledMessageDialog

def ShowMessage(msg, title='EasyPython'):
        drScrolledMessageDialog.ShowMessage(None, msg, title)

def GetFilePath(path):
        """Takes a path including a file name, and returns a tuple
        containing the path (minus file name), and just the file name."""
        if path.find("\\") == -1:
            return (path[:path.rfind("/") + 1], path[path.rfind("/") +1:path.rfind(".")])
        else:
            return (path[:path.rfind("\\") + 1], path[path.rfind("\\") + 1:path.rfind(".")])

def LoadDialogSizeAndPosition(dialog, dialogfile, defaultdir=''):
        if config.prefs.rememberdialogsizesandpositions:
            if not defaultdir:
                defaultdir = config.AppDataDir
            sizeposfile = defaultdir + '/' + dialogfile
            try:
                if os.path.exists(sizeposfile):
                    f = file(sizeposfile, 'rb')
                    text = f.read()
                    f.close()
                    x, y, px, py = map(int, text.split('\n'))
                    dialog.SetSize((x, y))
                    dialog.Move(wx.Point(px, py))
            except:
                drScrolledMessageDialog.ShowMessage(dialog, 'Error Loading Dialog Size.  The file: "%s" may be corrupt.'\
                                                    % sizeposfile, 'Error')
        dialog.Bind(wx.EVT_CLOSE, dialog.OnCloseW)

def SaveDialogSizeAndPosition(dialog, dialogfile, defaultdir=''):
        if config.prefs.rememberdialogsizesandpositions:
            try:
                if not defaultdir:
                    defaultdir = config.AppDataDir
                f = file(defaultdir + '/' + dialogfile, 'wb')
                x, y = dialog.GetSizeTuple()
                px, py = dialog.GetPositionTuple()
                f.write(str(x) + '\n' + str(y) + '\n' + str(px) + '\n' + str(py))
                f.close()
            except:
                drScrolledMessageDialog.ShowMessage(dialog, "Error Saving Dialog Size", 'Error')

def Ask(question, title='EasyPython'):
        answer = wx.MessageBox(question, title, wx.YES_NO | wx.ICON_QUESTION)
        return (answer == wx.YES)

#ugly hack: on windows and gtk, yes no behaves different (on gtk, you can escape with ESC, on gtk it is the other side
def AskPlatformDependent(question, title='EasyPython'):
        if config.PLATFORM_IS_WIN:
            ok = wx.OK
            stylemsgbox = wx.OK | wx.CANCEL
        else:
            ok = wx.YES
            stylemsgbox = wx.YES_NO

        answer = wx.MessageBox(question, title, stylemsgbox | wx.ICON_QUESTION)
        return answer == ok

def AskExitingEasyPython():
        answer = wx.MessageBox(u'你真的要退出EasyPython吗?', "EasyPython", wx.YES_NO | wx.ICON_QUESTION)
        if answer == wx.YES:
            sys.exit()

def Append_Menu(menu, id, s, LaunchesDialog = False, AmpersandAt = -1, absolutelabel=''):
        label = s
        item = wx.MenuItem(menu, id, label, label)
        menuiconfile = config.BitmapDir + "/16/" + s + ".png"
        if os.path.exists(menuiconfile):
            img = wx.Image(menuiconfile, wx.BITMAP_TYPE_PNG)
            bmp = wx.BitmapFromImage(img)
            item.SetBitmap(bmp)
        menu.AppendItem(item)


def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))                    