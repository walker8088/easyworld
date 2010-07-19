# -*- coding: utf-8 -*-
import wx

class XmlConsole(wx.TextCtrl) :
        def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TE_MULTILINE) :
                wx.TextCtrl.__init__(self, parent, id, pos, size, style)
                
	def AppendMessage(self, io, data) :
		if io == 'in' :
			color = '#CC3333'
		elif io == 'out' :
			color = '#3366CC'
		else :
			print "error message io type"
			return
		self.AppendText(io + ' : ' + data + '\n')
	
                