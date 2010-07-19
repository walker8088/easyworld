
# -*- coding: utf-8 -*-

import os, math, wx

from glob import glob
import event, actions

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient

# ############################################################                
class ChessBmps :
        def __init__(self) :
                imgpath = os.path.join('res', 'chinesechess' )
                
                self.BoardBmp = wx.Image(os.path.join(imgpath, 'board.bmp'), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
                self.MaskBmp  = wx.Image(os.path.join(imgpath, 'mask.bmp'), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
                
                self.PieceBmps = {}
                for item in ['p', 'r', 'n', 'c', 'b', 'k', 'a'] :
                        imgfile = os.path.join(imgpath, 'r' + item + '.bmp') 
                        self.PieceBmps[item] = wx.Image(imgfile, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
                        
                for item in ['p', 'r', 'n', 'c', 'b','k','a'] :
                        imgfile = os.path.join(imgpath, 'b' + item + '.bmp') 
                        self.PieceBmps[item.upper()] = wx.Image(imgfile, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
                        
        def GetBoardBmp(self) :
                return self.BoardBmp
        
        def GetPieceBmp(self, name) :
                return self.PieceBmps[name]
                
# ############################################################                
class CChessBoardPanel(wx.Window):
        def __init__(self, parent, bmps):
                wx.Window.__init__(self, parent, -1, wx.DefaultPosition, (500, 600))
                
                self.shapes = []
                
                self.scale = 1.0
                
                self.bmps = bmps
                
                #self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
                self.bg_bmp = bmps.GetBoardBmp()
                self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
                
                self.Bind(wx.EVT_SIZE,             self.OnSize)
                self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
                self.Bind(wx.EVT_PAINT,            self.OnPaint)
                self.Bind(wx.EVT_LEFT_DOWN,        self.OnLeftDown)
                self.Bind(wx.EVT_LEFT_UP,          self.OnLeftUp)
                #self.Bind(wx.EVT_MOTION,           self.OnMotion)
                self.Bind(wx.EVT_LEAVE_WINDOW,     self.OnLeaveWindow)
                
                
        def OnSize(self, evt) :
		sz = self.GetClientSize()
	        
                if sz.width <= self.bg_bmp.GetWidth() :
                        xScale = 1.0
                else :
                        xScale = float(sz.width) / self.bg_bmp.GetWidth()
                
                if sz.height <= self.bg_bmp.GetHeight() :     
                        yScale = 1.0
                else :
                        yScale = float(sz.height) / self.bg_bmp.GetHeight()
                
                self.scale = xScale
                if yScale < self.scale :
                        self.scale = yScale
                self.Refresh()
		#print "on size"

        def OnEraseBackground(self, evt):
                dc = evt.GetDC()
                if not dc:
                        dc = wx.ClientDC(self)
                        rect = self.GetUpdateRegion().GetBox()
                        dc.SetClippingRect(rect)
                self.DrawBackground(dc)
        
        # Fired whenever a paint event occurs
        def OnPaint(self, evt):
                dc = wx.PaintDC(self)
                self.PrepareDC(dc)
                sz = self.GetClientSize()
	        
                #dc.SetUserScale(self.scale, self.scale)
                
    
        # tile the background bitmap
	def DrawBackground(self, dc):
	        self.ClearBackground()
	        
                sz = self.GetClientSize()
	        
                dc.SetUserScale(self.scale, self.scale)
                
                startx = (sz.width - self.bg_bmp.GetWidth() * self.scale) / 2
                if startx < 0 :
                        startx = 0
                        
                starty = (sz.height - self.bg_bmp.GetHeight() * self.scale) / 2
                if starty < 0 :
                        starty = 0
                
		dc.DrawBitmap(self.bg_bmp, startx, starty)
		
        # Go through our list of shapes and draw them in whatever place they are.
        def DrawShapes(self, dc):
                for shape in self.shapes:
                        if shape.shown:
                                shape.Draw(dc)

        # This is actually a sophisticated 'hit test', but in this
        # case we're also determining which shape, if any, was 'hit'.
        def FindShape(self, pt):
                for shape in self.shapes:
                        if shape.HitTest(pt):
                                return shape
                return None

        # Left mouse button is down.
        def OnLeftDown(self, evt):
                # Did the mouse go down on one of our shapes?
                shape = self.FindShape(evt.GetPosition())

                # If a shape was 'hit', then set that as the shape we're going to
                # drag around. Get our start position. Dragging has not yet started.
                # That will happen once the mouse moves, OR the mouse is released.
                if shape:
                    self.dragShape = shape
                    self.dragStartPos = evt.GetPosition()

        # Left mouse button up.
        def OnLeftUp(self, evt):
                if not self.dragImage or not self.dragShape:
                    self.dragImage = None
                    self.dragShape = None
                    return

                # Hide the image, end dragging, and nuke out the drag image.
                self.dragImage.Hide()
                self.dragImage.EndDrag()
                self.dragImage = None

                if self.hiliteShape:
                    self.RefreshRect(self.hiliteShape.GetRect())
                    self.hiliteShape = None

                # reposition and draw the shape

                # Note by jmg 11/28/03 
                # Here's the original:
                #
                # self.dragShape.pos = self.dragShape.pos + evt.GetPosition() - self.dragStartPos
                #
                # So if there are any problems associated with this, use that as
                # a starting place in your investigation. I've tried to simulate the
                # wx.Point __add__ method here -- it won't work for tuples as we
                # have now from the various methods
                #
                # There must be a better way to do this :-)
                #
                
                self.dragShape.pos = (
                    self.dragShape.pos[0] + evt.GetPosition()[0] - self.dragStartPos[0],
                    self.dragShape.pos[1] + evt.GetPosition()[1] - self.dragStartPos[1]
                    )
                    
                self.dragShape.shown = True
                self.RefreshRect(self.dragShape.GetRect())
                self.dragShape = None

        # The mouse is moving
        def OnMotion(self, evt):
                # Ignore mouse movement if we're not dragging.
                if not self.dragShape or not evt.Dragging() or not evt.LeftIsDown():
                    return

                # if we have a shape, but haven't started dragging yet
                if self.dragShape and not self.dragImage:

                    # only start the drag after having moved a couple pixels
                    tolerance = 2
                    pt = evt.GetPosition()
                    dx = abs(pt.x - self.dragStartPos.x)
                    dy = abs(pt.y - self.dragStartPos.y)
                    if dx <= tolerance and dy <= tolerance:
                        return

                    # refresh the area of the window where the shape was so it
                    # will get erased.
                    self.dragShape.shown = False
                    self.RefreshRect(self.dragShape.GetRect(), True)
                    self.Update()

                    if self.dragShape.text:
                        self.dragImage = wx.DragString(self.dragShape.text,
                                                      wx.StockCursor(wx.CURSOR_HAND))
                    else:
                        self.dragImage = wx.DragImage(self.dragShape.bmp,
                                                     wx.StockCursor(wx.CURSOR_HAND))

                    hotspot = self.dragStartPos - self.dragShape.pos
                    self.dragImage.BeginDrag(hotspot, self, self.dragShape.fullscreen)

                    self.dragImage.Move(pt)
                    self.dragImage.Show()

                # if we have shape and image then move it, posibly highlighting another shape.
                elif self.dragShape and self.dragImage:
                    onShape = self.FindShape(evt.GetPosition())
                    unhiliteOld = False
                    hiliteNew = False

                    # figure out what to hilite and what to unhilite
                    if self.hiliteShape:
                        if onShape is None or self.hiliteShape is not onShape:
                            unhiliteOld = True

                    if onShape and onShape is not self.hiliteShape and onShape.shown:
                        hiliteNew = True

                    # if needed, hide the drag image so we can update the window
                    if unhiliteOld or hiliteNew:
                        self.dragImage.Hide()

                    if unhiliteOld:
                        dc = wx.ClientDC(self)
                        self.hiliteShape.Draw(dc)
                        self.hiliteShape = None

                    if hiliteNew:
                        dc = wx.ClientDC(self)
                        self.hiliteShape = onShape
                        self.hiliteShape.Draw(dc, wx.INVERT)

                    # now move it and show it again if needed
                    self.dragImage.Move(evt.GetPosition())
                    if unhiliteOld or hiliteNew:
                        self.dragImage.Show()
                
        # We're not doing anything here, but you might have reason to.
        # for example, if you were dragging something, you might elect to
        # 'drop it' when the cursor left the window.
        def OnLeaveWindow(self, evt):
                pass

# ############################################################                
class CChessGamePanel(wx.Panel) :
        def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize) :
                wx.Panel.__init__(self, parent, id, pos, size)
                
                self._mgr = wx.aui.AuiManager()
                self._mgr.SetManagedWindow(self)
                
                bmps = ChessBmps()
                tb = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, 
                                wx.TB_NOICONS | wx.TB_TEXT | wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_VERTICAL)
                tb.SetToolBitmapSize(wx.Size(32,32))
                tb.AddLabelTool(-1, u"协商", glob.getBitmap('quit'))
                tb.AddLabelTool(-1, u"开始", glob.getBitmap('quit'))
                tb.AddLabelTool(-1, u"求和", glob.getBitmap('quit'))
                tb.AddLabelTool(-1, u"认输", glob.getBitmap('quit'))
                tb.AddLabelTool(-1, u"重新开始", glob.getBitmap('quit'))
                tb.AddLabelTool(-1, u"红黑交换", glob.getBitmap('quit'))
		tb.AddLabelTool(-1, u"翻转棋盘", glob.getBitmap('quit'))
		tb.AddLabelTool(-1, u"保存记录", glob.getBitmap('quit'))
                tb.AddLabelTool(-1, u"打谱", glob.getBitmap('quit'))
		tb.AddLabelTool(-1, u"退出游戏", glob.getBitmap('quit'))
                tb.Realize()
                self._mgr.AddPane(tb, wx.aui.AuiPaneInfo().
                          Name("toolbar").Caption("Toolbar").ToolbarPane().Top().DockFixed(True).
                          TopDockable(True).BottomDockable(False))

                '''
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                
                btnsizer = wx.BoxSizer(wx.VERTICAL)
                btnsizer.AddStretchSpacer()
                btnsizer.Add(wx.Button(self, -1, u"协商"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
                btnsizer.Add(wx.Button(self, -1, u"开始"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
                btnsizer.Add(wx.Button(self, -1, u"求和"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
                btnsizer.Add(wx.Button(self, -1, u"认输"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
                btnsizer.Add(wx.Button(self, -1, u"保存记录"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
                btnsizer.Add(wx.Button(self, -1, u"重新开始"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
                btnsizer.Add(wx.Button(self, -1, u"退出游戏"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
                btnsizer.Add(wx.StaticText(self, -1, u"走棋记录:"), 0, wx.ALIGN_TOP|wx.ALL, 5)
              
                self.MoveLogList = wx.ListCtrl(self, -1, size = (-1, 300))
                btnsizer.Add(self.MoveLogList, 0, wx.ALIGN_CENTER|wx.ALL, 5)
                
                btnsizer.AddStretchSpacer()
                
                sizer.Add(btnsizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
                
                psizer = wx.BoxSizer(wx.VERTICAL)
                
                self.upInfo = wx.StaticText(self, -1, u"黑方:") 
                psizer.Add(self.upInfo, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                #boardbmp = bmps.GetBoardBmp()
                #self.boardBmp = wx.StaticBitmap(self, -1, boardbmp, (0, 0), (boardbmp.GetWidth(), boardbmp.GetHeight()))
                self.boardBmp = CChessBoardPanel(self, bmps)
                psizer.Add(self.boardBmp, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.downInfo = wx.StaticText(self, -1, u"红方:") 
                psizer.Add(self.downInfo, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                sizer.Add(psizer, 1, wx.ALIGN_LEFT|wx.ALL, 5)
                
                rsizer = wx.BoxSizer(wx.VERTICAL)
                
                rsizer.Add(wx.StaticText(self, -1, u"消息:"), 0, wx.ALIGN_TOP|wx.ALL, 2)
              
                self.MessageList = wx.ListCtrl(self, -1, size = (-1, 400))
                rsizer.Add(self.MessageList, 1, wx.ALIGN_TOP|wx.ALL|wx.EXPAND, 2)
                
                rsizer.Add(wx.StaticText(self, -1, u"人员:"), 0, wx.ALIGN_TOP|wx.ALL, 2)
              
                self.MemberList = wx.ListCtrl(self, -1, size = (-1, 400))
                rsizer.Add(self.MemberList, 1, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 2)
                
                rsizer.Add(wx.StaticText(self, -1, u"输入消息:"), 0, wx.ALIGN_TOP|wx.ALL, 2)
                self.inputText = wx.TextCtrl(self, -1, '')
                rsizer.Add(self.inputText, 0, wx.ALIGN_BOTTOM|wx.ALL|wx.EXPAND, 2)
              
                sizer.Add(rsizer, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 1)
                
                self.SetSizer(sizer)
                
                '''
                self.MemberList = wx.ListCtrl(self, -1, size = (100, 400))
                self._mgr.AddPane(self.MemberList, wx.aui.AuiPaneInfo().BestSize((100,-1)).
                                Name('member').Caption(u'人员列表').Right().CloseButton(False).Position(1))
                
                self.MessageList = wx.ListCtrl(self, -1, size = (100, 400))
                self._mgr.AddPane(self.MessageList, wx.aui.AuiPaneInfo().
                                Name('message').Caption(u'消息').Right().CloseButton(False).Position(2))
                self.inputText = wx.TextCtrl(self, -1, '')
                self._mgr.AddPane(self.inputText, wx.aui.AuiPaneInfo().BestSize((-1,30)).
                                Name('input').Caption(u'发送消息').Right().CloseButton(False).Position(3))
                
                boardbmp = bmps.GetBoardBmp()
                self.boardBmp = CChessBoardPanel(self, bmps)
                
                self._mgr.AddPane(self.boardBmp, wx.aui.AuiPaneInfo().Name('board').CenterPane())
                self._mgr.Update()
                
# ############################################################                
	