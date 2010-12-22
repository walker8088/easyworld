#   Programmer: Daniel Pozmanter
#   E-mail:     drpython@bluebottle.com
#   Note:       You must reply to the verification e-mail to get through.
#
#   Copyright 2003-2007 Daniel Pozmanter
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#    DrPython is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#PopUp

import wx.stc

import config, glob, utils

def OnPopUp(stc, event):
        stc.actiondict = SetUpPopUpActions(glob.MainFrame)

        if not glob.PopupMenuList:
            glob.PopupMenuList = ["Undo", "Redo", "<Separator>", "Cut", "Copy", "Paste", "Delete", "<Separator>", "Select All"]

        stc.PopUpMenu = wx.Menu()

        #Franz: added getlabel functions.

        x = 0
        l = len(glob.PopupMenuList)
        while x < l:
            try:
                if glob.PopupMenuList[x] == "<Separator>":
                    stc.PopUpMenu.AppendSeparator()
                elif glob.PopupMenuList[x].find("<DrScript>") > -1:
                    label = glob.PopupMenuList[x][glob.PopupMenuList[x].find(":")+1:]
                    try:
                        i = stc.grandparent.drscriptmenu.titles.index(label)
                        stc.PopUpMenu.Append(stc.grandparent.ID_SCRIPT_BASE+i, stc.grandparent.drscriptmenu.getdrscriptmenulabel(label))
                        stc.Bind(wx.EVT_MENU, stc.OnPopUpMenu, id=stc.grandparent.ID_SCRIPT_BASE+i)
                    except:
                        pass
                elif glob.PopupMenuList[x].find("<Plugin>") > -1:
                    label = glob.PopupMenuList[x][glob.PopupMenuList[x].find(":")+1:]
                    try:
                        i = stc.grandparent.PluginPopUpMenuLabels.index (label)
                        stc.grandparent.PluginPopUpMenuLabels.index(label)
                        stc.PopUpMenu.Append(stc.ID_POPUP_BASE+x, stc.grandparent.GetPluginMenuLabel(stc.grandparent.PluginPopUpMenuNames [i], label, label))
                        stc.Bind(wx.EVT_MENU, stc.OnPopUpMenu, id=stc.ID_POPUP_BASE+x)
                    except:
                        pass
                else:
                    utils.Append_Menu(stc.PopUpMenu, stc.ID_POPUP_BASE+x, glob.PopupMenuList[x])
                    stc.Bind(wx.EVT_MENU, stc.OnPopUpMenu, id=stc.ID_POPUP_BASE+x)
            except:
                #Error with PopUpMenu Item
                pass
            x = x + 1
            
        stc.PopupMenu(stc.PopUpMenu, event.GetPosition())
        stc.PopUpMenu.Destroy()

def OnPopUpMenu(stc, event):
        eid = event.GetId()
        label = stc.PopUpMenu.GetLabel(eid)

        #Franz: Remove Shortcut
        f = label.find ("\t")
        if f != -1:
            label = label [:f]
        #/Remove Shortcut

        if label in stc.actiondict:
            stc.actiondict[label](event)
        elif label in stc.stclabelarray:
            if label == 'Paste':
                stc.Paste()
            else:
                i = stc.stclabelarray.index(label)
                stc.CmdKeyExecute(stc.stcactionarray[i])
        else:
            #DrScript
            try:
                i = stc.grandparent.drscriptmenu.titles.index(label)
                stc.grandparent.drscriptmenu.OnScript(event)
            except:
                pass
            #Plugins
            try:
                i = stc.grandparent.PluginPopUpMenuLabels.index(label)
                stc.grandparent.PluginPopUpMenuFunctions[i](event)
            except:
                pass

def SetUpPopUpActions(frame):
    actiondictionary = {
    "Find":frame.OnMenuFind, 
    "Find Next":frame.OnMenuFindNext, 
    "Find Previous":frame.OnMenuFindPrevious,
    "Replace":frame.OnMenuReplace,
    "Indent":frame.OnIndentRegion, 
    "Dedent":frame.OnDedentRegion,
    "Toggle View Whitespace":frame.OnToggleViewWhiteSpace,
    "Check Syntax":frame.OnCheckSyntax,
    }

    return actiondictionary


