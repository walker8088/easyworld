# __init__.py

WAX_VERSION = "0.3.16"
WAX_VERSION_TUPLE = tuple(map(int, WAX_VERSION.split(".")))

__version__ = WAX_VERSION
__license__ = "BSD"
__copyright__ = "Copyright 2003-2005 Hans Nowak"
__author__ = "Hans Nowak (hans@zephyrfalcon.org)"

import sys

import core # builtin functions and such
from application import Application
from artprovider import ArtProvider
from bitmap import Bitmap, BitmapFromData, BitmapFromFile
from bitmapbutton import BitmapButton
from button import Button
from canvas import Canvas
from checkbox import CheckBox
from checklistbox import CheckListBox
from colordb import ColorDB
from combobox import ComboBox
from containers import Container # do we need to publish this?
from customdialog import CustomDialog
from dialog import Dialog, showdialog
from directorydialog import DirectoryDialog, ChooseDirectory
from dragdrop import FileDropTarget, TextDropTarget, URLDropTarget
from dropdownbox import DropDownBox
from filedialog import FileDialog
from filetreeview import FileTreeView
from findreplacedialog import FindReplaceDialog
from flexgridframe import FlexGridFrame
from flexgridpanel import FlexGridPanel
from font import Font
from fontdialog import FontDialog
from frame import Frame, HorizontalFrame, VerticalFrame
from grid import Grid
from gridframe import GridFrame
from gridpanel import GridPanel
from groupbox import GroupBox
from htmlwindow import HTMLWindow
from image import Image, AddImageHandler, AddAllImageHandlers, ImageAsBitmap
from imagelist import ImageList
from keys import keys
from label import Label
from line import Line
from listbox import ListBox
from listview import ListView, ListItemAttr
#from maskedtextbox import MaskedTextBox
from menu import Menu, MenuBar
from messagedialog import MessageDialog, ShowMessage
from mdiframes import MDIChildFrame, MDIParentFrame
from mousepointer import MousePointers
from notebook import NoteBook
from overlaypanel import OverlayPanel
from panel import Panel, HorizontalPanel, VerticalPanel
from plainframe import PlainFrame
from plainpanel import PlainPanel
from radiobutton import RadioButton
from scrollframe import ScrollFrame
from shell import PyCrust, PyCrustFilling
from simpleeditor import SimpleEditor
from splitter import Splitter
from statusbar import StatusBar
from styledtextbox import StyledTextBox
from systemsettings import SystemSettings
from textbox import TextBox
from textentrydialog import TextEntryDialog
from timer import Timer
from treelistview import TreeListView
from treeview import TreeView
from waxconfig import WaxConfig
from waxobject import WaxObject

if sys.platform != 'darwin':
    from togglebutton import ToggleButton
    # doesn't exist on the Mac?
    from sound import Sound
if sys.platform == 'win32':
    from taskbaricon import TaskBarIcon

# behavior injection
# XXX maybe this can be handled by the MetaWaxObject?
import types
classes = [obj for obj in globals().values()
           if type(obj) is types.ClassType and issubclass(obj, WaxObject)]
import inject
inject.inject(classes)

del types, inject, classes, obj
# we don't need these in the Wax namespace
