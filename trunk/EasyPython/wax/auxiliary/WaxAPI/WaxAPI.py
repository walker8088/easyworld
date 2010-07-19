#--------------------------------------------------------------------------------
# A window to view documentation on Wax/wx objects
#   Author: Jason Gedge
#
#   TODO:
#--------------------------------------------------------------------------------

import wax
from wax import *
import wx
import os
from types import ClassType, InstanceType
from htmlexport import name_mapping, write_module


#
# Build a class list that can be used with LoadFromNestedList
#
def BuildClassHierarchyDict(obj, accepted):
    temp = [(k, v) for k, v in obj.__dict__.items() if type(v) in accepted]
    temp.sort()

    l = []
    for k, v in temp:
        l.append( (k, k, hierarchial_build(v)) )
    return l

#
# Helper function for BuildClassHierarchyDict
#
def hierarchial_build(obj):
    l = []
    if hasattr(obj, '__bases__'):
        for cls in obj.__bases__:
            if cls is not object:
                a = cls.__name__
                l.append( (a, cls.__module__ + '.' + a, hierarchial_build(cls)) )
    return l


class WaxAPIFrame(Frame):
    def Body(self):
        # Create the controls and containers
        self.split_v = Splitter(self)
        self.split_h = Splitter(self.split_v)
        self.obj_list = TreeView(self.split_v, twist_buttons=1, has_buttons=1)
        self.mem_list = ListBox(self.split_h, selection='single')
        self.doc_lbl = Label(self.split_h, '', border='static', noresize=1)

        # Update the events
        self.mem_list.OnClick = self.mem_list_OnClick
        self.obj_list.OnSelectionChanged = self.obj_list_OnSelectionChanged

        # Split the controls
        self.split_h.Split(self.mem_list, self.doc_lbl, direction='h')
        self.split_v.Split(self.obj_list, self.split_h, direction='v')

        # Update tree with wax module
        self.FillTree(wax, [ClassType, InstanceType, waxobject.MetaWaxObject])

        # Create menus
        self.mb = MenuBar(self)
        self.mnu_file = Menu(self)
        self.mnu_file.Append('E&xport to HTML...', self.mnu_export)
        #self.mnu_file.Append('Show &private members', self.mnu_show_private, type='check')
        self.mnu_file.Append('Show &special members', self.mnu_show_special, type='check')
        self.mnu_file.AppendSeparator()
        self.mnu_file.Append('E&xit', self.mnu_exit)
        self.mb.Append(self.mnu_file, '&File')

        # Initialize options
        self.show_specials = False
        #self.show_privates = False

        # Finalize
        self.SetSize((600, 400))
        self.AddComponent(self.split_v, expand='both')
        self.Pack()

        self.split_v.SetSashPosition(175)
        self.split_h.SetSashPosition(200)

    def FillTree(self, module, accepted):
        """Adds all the items to the object tree"""
        self.module = module
        self.objects = BuildClassHierarchyDict(module, accepted)

        root = self.obj_list.AddRoot(module.__name__)
        self.obj_list.LoadFromNestedList(root, self.objects)
        self.obj_list.Expand( self.obj_list.GetRootItem() )

    def UpdateMembersList(self, obj):
        a = obj.__dict__
        self.obj = obj
        self.members = [ (x, x) for x in a if x[0] != '_' ] + \
                       [ (name_mapping[x][0], x) for x in a if self.show_specials and \
                                                               x.startswith('__') and \
                                                               x in name_mapping ] #+  \
                       #[ (x, x) for x in a if self.show_privates and x[0] == '_' and \
                       #                       x[1] != '_' and not x in name_mapping ] + \
                       #[ (x, x) for x in a if self.show_specials and x.startswith('__') and \
                       #                       not x in name_mapping ]

        self.members.sort()

        # Add these members to the list box
        self.mem_list.SetItems(self.members)

    def GetSignature(self, func):
        """Returns a string representing the function's signature"""
        #argnames, args, kwargs, defs = inspect.getargspec(function)

        sep = ','
        str = func.func_name + '(' + sep.join(func.func_code.co_varnames) + ')'
        return str

    def obj_list_OnSelectionChanged(self, event=None):
        item = event.GetItem()
        #obj = self.obj_list.GetItemText(item)

        data = self.obj_list.GetPyData(item)
        if data is None:
            data = self.obj_list.GetItemText(item)
        obj = eval(data)

        self.UpdateMembersList(obj)

        if obj.__doc__:
            self.doc_lbl.SetLabel(obj.__doc__)
        else:
            self.doc_lbl.SetLabel('No Documentation')

    def mem_list_OnClick(self, event=None):
        id = self.mem_list.GetSelection()
        item = self.members[id][1]

        if item in name_mapping:
            self.doc_lbl.SetLabel(name_mapping[ item ][1])
        else:
            obj = getattr(self.obj, item)
            if obj:
                doc = '%s\n------------------------------------\n%s'
                if obj.__doc__:
                    self.doc_lbl.SetLabel( doc % (self.GetSignature(obj), obj.__doc__.strip()) )
                else:
                    self.doc_lbl.SetLabel( doc % (self.GetSignature(obj), '') )
            else:
                self.doc_lbl.SetLabel('No Documentation')

#    def mnu_show_private(self, event):
#        self.show_privates = event.IsChecked()
#
    def mnu_show_special(self, event):
        self.show_specials = event.IsChecked()

    def mnu_exit(self, event):
        self.Close()
        
    def mnu_export(self, event):
        dlg = DirectoryDialog(self)
        dlg.SetPath(os.path.dirname(__file__))
        res = dlg.ShowModal()
        if res == 'ok':
            dir = dlg.GetPath()
            # I think this first bit (no directory) is impossible on windows?
            if not os.path.exists(dir):
                msg = MessageDialog(self, title="Directory Doesn't Exist",
                                    text="The directory does not exist. Would you like to create it?",
                                    yes_no=1, icon='exclamation')
                res = msg.ShowModal()
                if res == 'yes':
                    os.mkdir(dir)
                    write_module(wax, dir, [ClassType, InstanceType, waxobject.MetaWaxObject])
            else:
                write_module(wax, dir, [ClassType, InstanceType, waxobject.MetaWaxObject])


app = Application(WaxAPIFrame, title='Wax API Query')
app.Run()
