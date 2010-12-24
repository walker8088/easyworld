
import logging
import wx

import EpyGlob

# ############################################################                
class ActionItem :
        def __init__(self, parent, name, show = '', func = None, enabled = True, checked = False) :
                self.parent  = parent
                self.id      = wx.NewId()
                self.name    = name
                
                if show == '' :
                    self.show = name
                else:
                    self.show    = show
           
                self.func    = func
                self.enabled = enabled 
                self.checked = checked
                
                self.handlers = []
        
        def Enable(self, enabled = True) :
                self.enabled = enabled 
                self.Refresh()
                
        def IsEnabled(self) :
                return self.enabled
                
        def AppendToMenu(self, menu, handler = None, tmp = False) :
                menu.Append(self.id, self.show)
                menu.Enable(self.id, self.enabled)
                
                if not tmp :
                        self.handlers.append(menu)
                
                if not self.func :
                        return
                        
                if handler :
                        handler.Bind(wx.EVT_MENU, self.func, id = self.id)
                else :
                       self.parent.Bind(wx.EVT_MENU, self.func, id = self.id)
                
                
        def AppendToToolBar(self, toolbar, handler = None, tmp = False, is_check = False) :
                toolbar.AddLabelTool(self.id, self.show, EpyGlob.getBitmap(self.name))
                
                toolbar.EnableTool(self.id, self.enabled)
                
                if not tmp :
                        self.handlers.append(toolbar)
        
                if not self.func :
                        return
                
                if handler :
                        handler.Bind(wx.EVT_TOOL, self.func, id = self.id)
                else :
                        self.parent.Bind(wx.EVT_TOOL, self.func, id = self.id)
                
        def AppendToAuiToolBar(self, toolbar, handler = None, tmp = False, is_check = False) :
                toolbar.AddSimpleTool(self.id, self.show, EpyGlob.getBitmap(self.name))
                toolbar.EnableTool(self.id, self.enabled)
                
                if not tmp :
                        self.handlers.append(toolbar)
        
                if not self.func :
                        return
                
                if handler :
                        handler.Bind(wx.EVT_TOOL, self.func, id = self.id)
                else :
                        self.parent.Bind(wx.EVT_TOOL, self.func, id = self.id)
                
                
        def Refresh(self) :
                for handler in self.handlers :
                        if handler == None:
                                continue       
                        if isinstance(handler, wx.ToolBar):
                                handler.EnableTool(self.id, self.enabled)
                        elif isinstance(handler, wx.Menu):
                                handler.Enable(self.id, self.enabled)
                        
# ############################################################                
class CheckActionItem(ActionItem) :
        def __init__(self, parent, name, show, func, enabled = True, checked = False) :
                ActionItem.__init__(self, parent, name, show, func, enabled) 
                self.checked = checked
        
        def AppendToToolBar(self, toolbar, handler = None, tmp = False) :
                toolbar.AddCheckLabelTool(self.id, self.show, EpyGlob.getBitmap(self.name))
                toolbar.EnableTool(self.id, self.enabled)
                toolbar.ToggleTool(self.id, self.checked) 
                
                if not tmp :
                        self.handlers.append(toolbar)
        
                if not self.func :
                        return
                
                if handler :
                        handler.Bind(wx.EVT_TOOL, self.func, id = self.id)
                else :
                        self.parent.Bind(wx.EVT_TOOL, self.func, id = self.id)
        
        def Check(self, checked = True) :
                if self.checked != checked :
                        self.checked = checked
                        self.Refresh()
                        
        def IsChecked(self) :
                return self.cheked
        
        def CheckReverse(self) :
                self.checked = not self.checked
                self.Refresh()
                        
        def Refresh(self) :
                ActionItem.Refresh(self)
                for handler in self.handlers :
                        if handler == None:
                                continue       
                        if isinstance(handler, wx.ToolBar):
                                handler.ToggleTool(self.id, self.checked)
                        elif isinstance(handler, wx.Menu):
                                handler.Check(self.id, self.checked)
                
# ############################################################                                
class Actions :
        def __init__(self, parent) :
                self.parent = parent
                self.items_dict={}
        
        def __iter__(self):
                return self.items_dict.itervalues()

        def __contains__(self, name):
                return name in self.items_dict

        def __getitem__(self, name):
                return self.items_dict[name]

        def GetActions(self):
                """Return a list of items in the roster."""
                return self.items_dict.values()

        Actions = property(GetActions)
        
        def AddAction(self, name, show, func, enabled = True):
                item = ActionItem(self.parent, name, show, func, enabled)
                self.items_dict[item.name] = item
                return item
        
        def AddCheckAction(self, show, func, enabled = True, checked = False):
                item = CheckActionItem(self.parent, show, func, enabled, checked)
                self.items_dict[item.name] = item
                return item
        
        def RemoveAction(self, name):
                """Remove item from the roster."""
                del self.items_dict[name]
                
# ############################################################                
