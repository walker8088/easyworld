#!/usr/bin/python

import os, sys, threading, time, socket
import string, sets, struct, Queue

import pyaudio,speex

import wx

from twisted.internet import wxreactor
wxreactor.install()
    
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.application.internet import MulticastServer
from twisted.internet import threads 

APP_NAME = 'Easy Talk'
APP_VERSION = 'Version 0.2'

USER_LIST_EVENT = wx.NewEventType()
EVT_USER_LIST = wx.PyEventBinder(USER_LIST_EVENT, 1)  

USER_JOIN_EVENT = wx.NewEventType()
EVT_USER_JOIN = wx.PyEventBinder(USER_JOIN_EVENT, 1)  

USER_LEAVE_EVENT = wx.NewEventType()
EVT_USER_LEAVE = wx.PyEventBinder(USER_LEAVE_EVENT, 1)  

class UserActiveEvent(wx.PyCommandEvent):
    def __init__(self, eventType, eventSource, userName):
        wx.PyCommandEvent.__init__(self, eventType, id = -1)
        self.eventSource = eventSource
        self.userName = userName

class UserListEvent(wx.PyCommandEvent):
    def __init__(self, eventSource, userList):
        wx.PyCommandEvent.__init__(self, USER_LIST_EVENT, id = -1)
        self.eventSource = eventSource
        self.userList = userList

TALK_RING_EVENT = wx.NewEventType()
EVT_TALK_RING = wx.PyEventBinder(TALK_RING_EVENT, 1)  

TALK_RING_BACK_EVENT = wx.NewEventType()
EVT_TALK_RING_BACK = wx.PyEventBinder(TALK_RING_BACK_EVENT, 1)  

TALK_ACCEPT_EVENT = wx.NewEventType()
EVT_TALK_ACCEPT = wx.PyEventBinder(TALK_ACCEPT_EVENT, 1)  

TALK_HANGUP_EVENT = wx.NewEventType()
EVT_TALK_HANGUP = wx.PyEventBinder(TALK_HANGUP_EVENT, 1)  

TALK_TIME_OUT_EVENT = wx.NewEventType()
EVT_TALK_TIME_OUT = wx.PyEventBinder(TALK_TIME_OUT_EVENT, 1)  

class TalkEvent(wx.PyCommandEvent):
        def __init__(self, eventType, eventSource):
                wx.PyCommandEvent.__init__(self, eventType, id = -1)
                self.eventSource = eventSource
                self.peerAddr = None
                self.talkToAddr = None
                
class TalkAcceptEvent(wx.PyCommandEvent):
        def __init__(self, accept, eventSource):
                wx.PyCommandEvent.__init__(self, TALK_ACCEPT_EVENT, id = -1)
                self.eventSource = eventSource
                self.accept = accept

class Talker :
        LIVE_COUNT = 3
        
        def __init__(self, name, address) :
                self.name = name
                self.address = address
                self.active()
        
        def active(self) :
                self.leftLife = self.LIVE_COUNT
        
        def dead(self) :
                self.leftLife -= 1
                if self.leftLife <= 0 :
                        return True
                else :
                        return False
                
                     
class MulticastGroupMemberManager(DatagramProtocol):
        MULTICAST_GROUP = '224.0.0.1'
        
        def __init__(self, parent) :
                self.group = None
                self.memberList = []
                self.connector = None
                self.parent = parent
                
        def startManager(self, port, interface = '') :
                try :
                        self.connector = reactor.listenMulticast(port, self, interface)  
                        
                        #print self.connector.getHost()        
                        self.port = port
                        
                        self.livingThread = LoopingCall(self.living)
                        self.livingThread.start(10)
                        
                        return True
                except Exception, e :
                        print e
                        self.connector = None
                        return False
                        
        def stopManager(self) :
                if self.connector != None :
                        self.livingThread.stop()
                        self.connector.stopListening()
                        if self.group != None :
                                self.leaveGroup()
        
        def setGroupUser(self, group) :
                if group.strip() == '':
                        return False
                self.transport.write("easytalk join %s" % (group), (self.MULTICAST_GROUP, self.port))
                self.group = group
                return True
                
        def leaveGroup(self) :
                self.transport.write("easytalk leave %s" % (self.group), (self.MULTICAST_GROUP, self.port))
                self.group =  None
                
        def findUser(self, name) :       
                for item in self.memberList :       
                        if item.name == name :
                                return item
                return None
                
        def startProtocol(self):
                self.transport.joinGroup(self.MULTICAST_GROUP)
        
        def living(self) :
                if self.group != None: 
                        self.transport.write("easytalk join %s" % (self.group), (self.MULTICAST_GROUP, self.port))
                for item in self.memberList :       
                        if item.dead() :
                                self.memberList.remove(item)
                                evt = UserActiveEvent(USER_LEAVE_EVENT, self, item.name)
                                self.parent.ProcessEvent(evt)
                
        def datagramReceived(self, datagram, address):
                print "Received:" + repr(datagram) + " From Address:" + str(address) 
                cmd = string.split(datagram)
                if len(cmd) < 3 or cmd[0] != 'easytalk':
                        return
                if cmd[1] == 'join' :
                        findItem = False        
                        for item in self.memberList :       
                                if item.name == cmd[2] and item.address == address :
                                        item.active()
                                        findItem = True
                        if not findItem :
                                item = Talker(cmd[2], address)
                                self.memberList.append(item)
                                evt = UserActiveEvent(USER_JOIN_EVENT, self, cmd[2])
                                self.parent.ProcessEvent(evt)
                elif cmd[1] == 'leave' :
                        findItem = False        
                        for item in self.memberList :       
                                if item.name == cmd[2] and item.address == address :
                                        self.memberList.remove(item)
                                        evt = UserActiveEvent(USER_LEAVE_EVENT, self, cmd[2])
                                        self.parent.ProcessEvent(evt)
                                        findItem = True
                        if not findItem :
                                print "Not Find :" + cmd[2] + " From Address:" + str(address) 
                
                else :
                        print "Error Received:" + repr(datagram) + " From Address:" + str(address) 

class UdpGroupMemberManager(DatagramProtocol):  
        def __init__(self, parent) :
                self.group = None
                self.memberList = []
                self.connector = None
                self.parent = parent
                
        def startManager(self, serverAddress, port, interface = '') :
                try :
                        self.connector = reactor.listenUDP(port, self, interface)                    
                        #print self.connector.getHost()        
                        self.serverAddress = serverAddress
                        
                        self.livingThread = LoopingCall(self.living)
                        self.livingThread.start(10)
                        
                        return True
                except Exception, e :
                        print e
                        self.connector = None
                        return False
                        
        def stopManager(self) :
                if self.connector != None :
                        self.livingThread.stop()
                        if self.group != None :
                                self.leaveGroup()
                        self.connector.stopListening()
                
        def setGroupUser(self, group) :
                if group.strip() == '':
                        return False
                self.transport.write("easytalk join %s" % (group), self.serverAddress)
                self.group = group
                return True
                
        def leaveGroup(self) :
                self.transport.write("easytalk leave %s" % (self.group), self.serverAddress)
                self.group =  None
                
        def findUser(self, name) :       
                for item in self.memberList :       
                        if item.name == name :
                                return item
                return None
                
        def living(self) :
                if self.group != None: 
                        self.transport.write("easytalk join %s" % (self.group), self.serverAddress)
                
        def datagramReceived(self, datagram, address):
                print "Received:" + repr(datagram) + " From Address:" + str(address) 
                cmd = string.split(datagram)
                if len(cmd) < 3 or cmd[0] != 'easytalk':
                        return
                if cmd[1] == 'join' :
                        talker = string.split(cmd[2],":")
                        print talker
                        findItem = False        
                        for item in self.memberList :       
                                if item.name == talker[0] and item.address[0] == talker[1] :
                                        item.active()
                                        findItem = True
                        if not findItem :
                                item = Talker(talker[0], (talker[1], int(talker[2])))
                                self.memberList.append(item)
                                evt = UserActiveEvent(USER_JOIN_EVENT, self, talker[0])
                                self.parent.ProcessEvent(evt)
                elif cmd[1] == 'leave' :
                        talker = string.split(cmd[2],":")
                        findItem = False        
                        for item in self.memberList :       
                                if item.name == talker[0] and item.address[0] == talker[1] :
                                        self.memberList.remove(item)
                                        evt = UserActiveEvent(USER_LEAVE_EVENT, self, talker[0])
                                        self.parent.ProcessEvent(evt)
                                        findItem = True
                        if not findItem :
                                print "Not Find :" + talker[0] + " From Address:" + str(address) 
                elif cmd[1] == 'members' :
                        members = cmd[2:]
                        self.memberList = []
                        for item in members :
                                params = string.split(item, ':')
                                talker = Talker(params[0], (params[1], int(params[2])))
                                self.memberList.append(talker)
                        
                        evt = UserListEvent(self, self.memberList)
                        self.parent.ProcessEvent(evt)
                else :
                        print "Error Received:" + repr(datagram) + " From Address:" + str(address) 
                
class TalkSessionManager(DatagramProtocol) :
        def __init__(self, parent) :
                self.parent = parent
                self.state = "stoped"
                self.peerAddr = None
                self.peerTalkAddr = None
                self.timer = None
                self.connector = None
                
        def initStatus(self) :
                self.peerAddr = None
                self.peerTalkAddr = None
 
                self.state = "listening"
                
                if self.timer != None :
                        self.timer.cancel()
                        self.timer = None
        
        def startManager(self, port) :
                try :
                        self.connector = reactor.listenUDP(port, self)
                        #sock = self.connector.getHandle()                                                        
                        self.port = port
                        self.initStatus()
                        return True
                except Exception, e :
                        self.connector = None
                        return False

        def stopManager(self) :
                #TODO
                #if self.state != "listening" :
                #        self.hangUp()
                        
                self.connector.stopListening()
                
                self.state = "stoped"
                self.peerAddr = None
                self.peerTalkAddr = None
                self.connector = None
        
        def call(self, peerAddr) : 
                self.peerAddr = peerAddr 
        
                self.transport.write("call", self.peerAddr)
                self.state = "calling"
                
                self.timer = threading.Timer(2, self.onTimeOut)
                self.timer.start()
                             
        def onTimeOut(self) :
                evt = TalkEvent(TALK_TIME_OUT_EVENT, self)
                self.parent.ProcessEvent(evt) 
                self.initStatus()
                
        def onCall(self, fromAddr) :               
                self.peerAddr = fromAddr
                self.transport.write("ring", self.peerAddr)
                
                self.state = "ringing"
                
                evt = TalkEvent(TALK_RING_EVENT, self)
                self.parent.ProcessEvent(evt) 

                self.timer = threading.Timer(20, self.onTimeOut)
                self.timer.start()
                
        def onRingBack(self) :
                self.timer.cancel()
                self.timer = None
        
                self.state = "ringing"
                evt = TalkEvent(TALK_RING_BACK_EVENT, self)
                self.parent.ProcessEvent(evt) 

                self.timer = threading.Timer(20, self.onTimeOut)
                self.timer.start()
                
        def answerCall(self, accept = True, talkPort = None) :
                if self.timer != None :
                        self.timer.cancel()
                        self.timer = None
                if accept :
                        self.talkPort = talkPort
                        cmd = "accept %d" % (self.talkPort)
                        self.transport.write(cmd, self.peerAddr) 
                        self.state = "talking"                 
                        evt = TalkAcceptEvent(True, self)
                        self.parent.ProcessEvent(evt)
                else :
                        self.transport.write("reject", self.peerAddr)
                        evt = TalkAcceptEvent(False, self)
                        self.parent.ProcessEvent(evt)
                        self.initStatus()
         
        def onAccept(self, peerTalkPort) :
                if self.timer != None :
                        self.timer.cancel()
                        self.timer = None
               
                self.peerTalkAddr = (self.peerAddr[0],peerTalkPort)

                self.state = "talking"                 
                evt = TalkAcceptEvent(True, self)
                self.parent.ProcessEvent(evt)
                
        def onReject(self) :
                if self.timer != None :
                        self.timer.cancel()
                        self.timer = None
                        
                evt = TalkAcceptEvent(False, self)
                self.parent.ProcessEvent(evt) 
                self.initStatus()
                                                
        def hangUp(self) :
                self.transport.write("hangup", self.peerAddr)
                self.onHangUp()
                
        def onHangUp(self) :        
                if self.timer != None :
                        self.timer.cancel()
                        self.timer = None
                
                evt = TalkEvent(TALK_HANGUP_EVENT, self)
                self.parent.ProcessEvent(evt)
                
                self.initStatus()
        
        def datagramReceived(self, data, (host, port)):
                #print "datagramReceived begin."
                print "received [%s] from %s:%d" % (data, host, port)
                
                cmd = string.split(data)
                if len(cmd) == 0 :
                        return
                if cmd[0] == 'error' :
                        return
                        
                if self.peerAddr != None :
                        if self.peerAddr[0] != host or self.peerAddr[1] != port :
                                self.transport.write('error', (host, port)) 
                                return
                        elif cmd[0] == 'ring' :
                                self.onRingBack()
                        elif cmd[0] == 'hangup' :
                                self.onHangUp()
                        elif cmd[0] == 'reject' :
                                self.onReject()
                        elif cmd[0] == 'accept' and len(cmd) == 2 :
                                self.onAccept(int(cmd[1]))
                        else :
                                self.transport.write('error', self.peerAddr)               
                        
                elif cmd[0] == "call":
                        self.onCall((host, port))
                else :
                        self.transport.write('error', (host, port))               
                       
                #print "datagramReceived end."
          

class VoiceChatManager(DatagramProtocol):
        def __init__ (self):
                
                self._soundRate = 8000
                self._chunkSize = 160
                self._chunkPack = '160h'
                
                self.decoder = speex.new()
                self.encoder = speex.new()
                  
                self._voicePlayQueue = Queue.Queue(200)
                self._voicePlayed = False  
             
                self.sendCount = 0
                self.recvCount = 0
             
                self.connector = None
                self.destAddr = []
                
                self.voiceSendThread = LoopingCall(self.sendVoice)
                self.voicePlayThread = LoopingCall(self.playVoice)
                
                self.sendVoiceEnabled = True
                self.playVoiceEnabled = True
                self.echoMode = False
                
                self._inputStream = None
                self._outputStream = None

        def startManager(self, port) :
                try :
                        self.connector = reactor.listenUDP(port, self)
                        self.port = port
                        return True
                except Exception, e :
                        print e
                        self.connector = None
                        return False
            
        def stopManager(self) :
                self.connector.stopListening()
    
        def enableSendVoice(self, yes) :
                self.sendVoiceEnabled = yes

        def enablePlayVoice(self, yes) :
                self.playVoiceEnabled = yes

        def enableEchoMode(self, yes) :
                self.echoMode = yes

        def getStatusInfo(self) :
                return (self.sendCount, self.recvCount, self._voicePlayQueue.qsize())
        
        def startVoiceWaitPeerAddress(self, peerIP) :
                self.destAddr = []
                self.destAddr.append(peerIP)
        
        def startVoice(self, destAddr) :  
                self.sendCount = 0
                self.recvCount = 0
             
                self._inputStream = pyaudio.PyAudio().open(format = pyaudio.paInt16,
                                                channels = 1,
                                                rate = self._soundRate,
                                                input = True,
                                                frames_per_buffer = self._chunkSize)
                                        
                self._outputStream = pyaudio.PyAudio().open(format = pyaudio.paInt16,
                                                channels = 1,
                                                rate = self._soundRate,
                                                output = True,
                                                frames_per_buffer = self._chunkSize)
                       
                self.destAddr = destAddr
                
                self.voiceSendThread.start(0.020)
                self.voicePlayThread.start(0.020)
                
        def stopVoice(self) :    
                self.destAddr = []
                
                if self._inputStream != None :
                        self.voiceSendThread.stop()
                        self._inputStream.close()
                        
                if self._outputStream != None :
                        self.voicePlayThread.stop()
                        self._outputStream.close()
                        
        def decode(self, data) :
                frames = self.decoder.decode(data)
                newdata = struct.pack(self._chunkPack, *frames)
                return newdata    
            
        def encode(self, data) :      
                frames = list(struct.unpack(self._chunkPack, data))
                newdata = self.encoder.encode(frames)
                return newdata
            
        def playVoice(self) : 
                if self._voicePlayed == False :
                        return
                        
                frames = self._chunkSize * 4 #self._outputStream.get_write_available()        
                while frames > 0 :
                        try :
                                data = self._voicePlayQueue.get_nowait()          
                        except Queue.Empty:
                                self._voicePlayed = False
                                print "voice play stoped."
                                return

                        newdata = self.decode(data) 
                        self._outputStream.write(newdata)
                        frames -= self._chunkSize
                        #print frames
                        
        def sendVoice(self) :
                #print "sendVoice begin."     
                if (not self.sendVoiceEnabled) or self.echoMode:
                        return 
                frames = self._inputStream.get_read_available()
                while frames > 0 :
                        try :
                                data = self._inputStream.read(self._chunkSize) 
                        except Exception, e:
                                #print e #"buffer overflow skip it."
                                return       
                        newdata = self.encode(data)
                        self.transport.write(newdata, self.destAddr)
                        self.sendCount += 1 
                        #print "sended: ", self.sendCount
                        frames -= self._chunkSize
                        #print frames
                #end while
                #print "sendVoice end."        
                             
        def datagramReceived(self, data, (host, port)):
                #print "datagramReceived begin."
                if self.echoMode :
                        self.transport.write(data, (host, port))
                        
                addrLen = len(self.destAddr)
                if addrLen == 2 and self.playVoiceEnabled : 
                        if (self.destAddr[0] != host) or (self.destAddr[1] != port) :
                                return
                                
                        self.recvCount += 1        
                        
                        #print "received [%d]" % (self.recvCount)
                        try :        
                                self._voicePlayQueue.put_nowait(data)
                        except Exception, e:
                                print e
                                
                        if (not self._voicePlayed) and self._voicePlayQueue.qsize() >= 10 : 
                                print "voice play started."
                                self._voicePlayed = True

                elif (addrLen == 1) and (self.destAddr[0] == host) :
                        self.startVoice((host, port))        
                #print "datagramReceived end."

class SoundPlayThread(threading.Thread):
        def __init__(self, soundFile):
                threading.Thread.__init__(self)
                self.soundFile = soundFile
                self.stoped = False
                self.start()
 
        def run(self):
                while not self.stoped : 
                        wx.Sound.PlaySound(self.soundFile, wx.SOUND_SYNC)        
                        if not self.stoped :
                                timer.sleep(1)
  
class MyTaskBarIcon(wx.TaskBarIcon):	
	ID_MenuExit = wx.NewId()

	def __init__(self, frame):
		wx.TaskBarIcon.__init__(self)	
		self.frame = frame	
		self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnTaskBarClick)
                #self.Bind(wx.EVT_MENU, self.OnMenuExit, id=self.ID_MenuExit)

        def ShowIcon(self, yes = True) :
                if yes :
                        self.SetIcon(wx.Icon(name='EasyTalk.ico', type=wx.BITMAP_TYPE_ICO), APP_NAME)
		elif self.IsIconInstalled():
                        self.RemoveIcon() 
        # override	
        #def CreatePopupMenu(self):
	#	menu = wx.Menu()		
        #        menu.Append(self.ID_MenuExit, '&Exit')
        #        return menu
                
	def OnTaskBarClick(self, event):
		if self.frame.IsIconized():
                        self.frame.Iconize(False)
                if not self.frame.IsShown():
			self.frame.Show(True)
		self.frame.Raise()
                self.ShowIcon(False)
        
        #def OnMenuExit(self, event):
	#	self.frame.Close()
	       

class SetupDialog(wx.Dialog):
    def __init__(
            self, parent = None, ID = -1, title = 'Setup', size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Talk Server Address:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self._serverAddrTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
        box.Add(self._serverAddrTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Talk   Server    Port:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self._serverPortTextCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
        box.Add(self._serverPortTextCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def doSetup(self, serverAddr) :
        self._serverAddrTextCtrl.SetValue(serverAddr[0])
        self._serverPortTextCtrl.SetValue(str(serverAddr[1])) 
        self.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = self.ShowModal()
    
        if val == wx.ID_OK:
                return (True, 
						(self._serverAddrTextCtrl.GetValue(),int(self._serverPortTextCtrl.GetValue()))
					)
        else :
                return (False,)
                   
class MainFrame(wx.Frame):
        ID_CALL     = wx.NewId()  
        ID_HANG_UP  = wx.NewId()  
        ID_ANSWER   = wx.NewId()  
        ID_REJECT   = wx.NewId()
        ID_SETUP    = wx.NewId()
        ID_STIMER   = wx.NewId()
        
        def __init__(self, parent, id=-1, title = APP_NAME, pos=wx.DefaultPosition,
                 size=(360, 230), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN):

                wx.Frame.__init__(self, parent, id, title, pos, size, style)
                
                icon = wx.Icon("easytalk.ico", wx.BITMAP_TYPE_ICO)
        	self.SetIcon(icon)
        	
                sizer = wx.BoxSizer(wx.VERTICAL)
                
                label = wx.StaticText(self, -1, '\n' + APP_NAME + ' ' + APP_VERSION)
                sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.userList = wx.ListBox(self, -1, size = (350, 200), style = wx.LB_SINGLE)
                sizer.Add(self.userList, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        
                box = wx.BoxSizer(wx.HORIZONTAL)

                label = wx.StaticText(self, -1, "My Address")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self._myAddrCtrl = wx.TextCtrl(self, -1, "", size=(180,-1), style = wx.TE_PROCESS_ENTER)
                #myIp = socket.gethostbyname(socket.gethostname())
                self._myAddrCtrl.SetValue(socket.gethostname())
                #self._myAddrCtrl.Disable()
                box.Add(self._myAddrCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.sendVoiceCheckBox = wx.CheckBox(self, -1, "MIC Phone")
                self.sendVoiceCheckBox.SetValue(True)
                box.Add(self.sendVoiceCheckBox, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
           
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

                box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(self, -1, "To Address")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self._toAddrCtrl = wx.TextCtrl(self, -1, "", size=(180,-1))
                box.Add(self._toAddrCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
               
                self.playVoiceCheckBox = wx.CheckBox(self, -1, "Speaker   ")
                self.playVoiceCheckBox.SetValue(True)
                box.Add(self.playVoiceCheckBox, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(self, -1, "                ")
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.autoAnswerCheckBox = wx.CheckBox(self, -1, "Auto Answer")
                #self.autoAnswerCheckBox.SetValue(True)
                box.Add(self.autoAnswerCheckBox, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.echoModeCheckBox = wx.CheckBox(self, -1, "Echo Mode(For Test Only)")
                box.Add(self.echoModeCheckBox, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                     
                sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                
                btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        
                self.btnCall = wx.Button(self, self.ID_CALL, "Call")
                self.btnCall.Enable()
                btnsizer.Add(self.btnCall, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.btnHangUp = wx.Button(self, self.ID_HANG_UP, "Hang Up")
                self.btnHangUp.Disable()
                btnsizer.Add(self.btnHangUp, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.btnAnswer = wx.Button(self, self.ID_ANSWER, "Answer")
                self.btnAnswer.Disable()
                btnsizer.Add(self.btnAnswer, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                self.btnReject = wx.Button(self, self.ID_REJECT, "Reject")
                self.btnReject.Disable()
                btnsizer.Add(self.btnReject, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
				
                self.btnSetup = wx.Button(self, self.ID_SETUP, "Setup")
                btnsizer.Add(self.btnSetup, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

                sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
         
                self._statusBar = self.CreateStatusBar(1, 0)
           
                self.SetSizer(sizer)
                sizer.Fit(self)
        
                self.SetBackgroundColour(wx.Colour(220, 220, 220))
                self.Center()
                
                self.taskBarIcon = MyTaskBarIcon(self)
                self.taskBarIcon.ShowIcon(False)
                
                self.statusTimer = wx.Timer(self, self.ID_STIMER)
                
                self.Bind(wx.EVT_TIMER, self.onTimer, self.statusTimer)
                
                self.Bind(wx.EVT_TEXT_ENTER, self.onChangeMyName, self._myAddrCtrl)
                
                self.Bind(wx.EVT_LISTBOX, self.onSelectUser, self.userList)
                
                self.Bind(wx.EVT_BUTTON, self.onBtnCall, self.btnCall)
                self.Bind(wx.EVT_BUTTON, self.onBtnHangUp, self.btnHangUp)
                self.Bind(wx.EVT_BUTTON, self.onBtnAnswer, self.btnAnswer)
                self.Bind(wx.EVT_BUTTON, self.onBtnReject, self.btnReject)
                self.Bind(wx.EVT_BUTTON, self.onBtnSetup,  self.btnSetup)
				
                
                self.Bind(wx.EVT_CHECKBOX, self.onSendVoiceChanged, self.sendVoiceCheckBox)
                self.Bind(wx.EVT_CHECKBOX, self.onPlayVoiceChanged, self.playVoiceCheckBox)
                self.Bind(wx.EVT_CHECKBOX, self.onEchoModeChanged, self.echoModeCheckBox)
                
                self.Bind(EVT_USER_JOIN,    self.onUserJoin)
                self.Bind(EVT_USER_LEAVE,   self.onUserLeave)
                self.Bind(EVT_USER_LIST,    self.onUserList)
                
                self.Bind(EVT_TALK_RING,      self.onTalkRing)
                self.Bind(EVT_TALK_RING_BACK, self.onTalkRingBack)
                self.Bind(EVT_TALK_ACCEPT,    self.onTalkAccept)
                self.Bind(EVT_TALK_HANGUP,    self.onTalkHangUp)
                self.Bind(EVT_TALK_TIME_OUT,  self.onTalkTimeOut)
                
                self.Bind(wx.EVT_CLOSE, self.OnClose)
                self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) 
                
                self.soungPlayThread = None
                '''
                self.groupManager = GroupMemberManager(self)
                if not self.groupManager.startManager(8008, myIp) :
                        dlg = wx.MessageDialog(self, 'EasyTalk could not listen on UDP multicast port 8008, exited',
                                'Message Alert', wx.OK | wx.ICON_INFORMATION )
                        dlg.ShowModal()
                        sys.exit(-1)
                '''
                self.groupManager = UdpGroupMemberManager(self)
                if not self.groupManager.startManager(('192.168.100.1', 8008), 8008) :
                        dlg = wx.MessageDialog(self, 'EasyTalk could not listen on UDP multicast port 8008, exited',
                                'Message Alert', wx.OK | wx.ICON_INFORMATION )
                        dlg.ShowModal()
                        sys.exit(-1)
                
                self.groupManager.setGroupUser(socket.gethostname())
                
                self.sessionManager = TalkSessionManager(self)
                if not self.sessionManager.startManager(9000) :
                        dlg = wx.MessageDialog(self, 'EasyTalk could not listen on UDP port 9000, exited',
                                'Message Alert', wx.OK | wx.ICON_INFORMATION )
                        dlg.ShowModal()
                        sys.exit(-1)
                        
                self.talkManager = VoiceChatManager()
                if not self.talkManager.startManager(9001) :
                        dlg = wx.MessageDialog(self, 'EasyTalk could not listen on UDP port 9001, exited.',
                                'Message Alert', wx.OK | wx.ICON_INFORMATION)
                        dlg.ShowModal()
                        sys.exit(-1)
                
        def onChangeMyName(self, event) :
                newName = self._myAddrCtrl.GetValue().strip().replace(' ', '_') 
                self._myAddrCtrl.SetValue(newName) 
                self.groupManager.leaveGroup()
                time.sleep(0.5)
                self.groupManager.setGroupUser(newName)
                
        def onSelectUser(self, event) :
                if self.userList.GetSelection() < 0 :
                        return 
                talker = self.groupManager.findUser(self.userList.GetStringSelection())
                self._toAddrCtrl.SetValue(talker.address[0])
                
        def onUserJoin(self, event) :
                self.userList.Append(event.userName)
                
        def onUserLeave(self, event) :
                index = self.userList.FindString(event.userName)
                if index >= 0 :
                        self.userList.Delete(index)
        
        def onUserList(self, event) :
                self.userList.Clear()
                for item in self.groupManager.memberList :
                        self.userList.Append(item.name)
                
        def onBtnCall(self, evt) :
                toAddr = self._toAddrCtrl.GetValue()
                if len(toAddr) == 0 :
                        dlg = wx.MessageDialog(self, 'Please specify To Address.','Message Alert',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
                        dlg.ShowModal()
                else :
                        self.sessionManager.call((self._toAddrCtrl.GetValue(), 9000))
                        self.btnCall.Disable()
                
        def onBtnHangUp(self, evt) :
                self.sessionManager.hangUp()
        
        def onBtnAnswer(self, evt) :
                self.sessionManager.answerCall(True, self.talkManager.port)
                 
        def onBtnReject(self, evt) :
                self.sessionManager.answerCall(False)
        
        def onBtnSetup(self, evt) :
                dlg = SetupDialog()
                result = dlg.doSetup(self.groupManager.serverAddress)
                if result[0] == True:
                    self.groupManager.serverAddress = result[1]
				
        def onSendVoiceChanged(self, evt) :
                self.talkManager.enableSendVoice(self.sendVoiceCheckBox.GetValue())
                
        def onPlayVoiceChanged(self, evt) :
                self.talkManager.enablePlayVoice(self.playVoiceCheckBox.GetValue())
        
        def onEchoModeChanged(self, evt) :
                self.talkManager.enableEchoMode(self.echoModeCheckBox.GetValue())
                
        def onTalkRing(self, event) :
                callMgr = event.eventSource
                self._toAddrCtrl.SetValue(self.sessionManager.peerAddr[0])
                wx.Sound.PlaySound("resource\\ring.wav", wx.SOUND_ASYNC)
                #self.soungPlayThread = SoundPlayThread("ring.wav")
                self.btnCall.Disable()
                self.btnHangUp.Disable()
                self.btnAnswer.Enable()
                self.btnReject.Enable()
                self.taskBarIcon.OnTaskBarClick(event)
                if self.autoAnswerCheckBox.GetValue() :
                        self.onBtnAnswer(event) 
        
        def onTalkRingBack(self, event) :                
               wx.Sound.PlaySound("resource\\ringback.wav", wx.SOUND_ASYNC)
               #self.soungPlayThread = SoundPlayThread("ringback.wav")
               self.btnCall.Disable()
               self.btnHangUp.Enable()
               self.btnAnswer.Disable()
               self.btnReject.Disable()
        
        def onTalkAccept(self, event) :
                if event.accept :
                        callMgr = event.eventSource
                        if callMgr.peerTalkAddr != None :
                                #client mode
                                self.talkManager.startVoice(callMgr.peerTalkAddr)
                        else :
                                #server mode
                                self.talkManager.startVoiceWaitPeerAddress(callMgr.peerAddr[0])    
                        
                        self.btnCall.Disable()
                        self.btnHangUp.Enable()
                        self.btnAnswer.Disable()
                        self.btnReject.Disable()
                        self.statusTimer.Start(1000)
                else :
                        self.btnCall.Enable()
                        self.btnHangUp.Disable()
                        self.btnAnswer.Disable()
                        self.btnReject.Disable()
                        
        def onTalkHangUp(self, event) :
                print "onHangUp"
                self.talkManager.stopVoice()
                self.btnCall.Enable()
                self.btnHangUp.Disable()
                self.btnAnswer.Disable()
                self.btnReject.Disable()
                self.statusTimer.Stop()
        
        def onTalkTimeOut(self, event) :
                print "onTalkTimeOut"
                self.btnCall.Enable()
                self.btnHangUp.Disable()
                self.btnAnswer.Disable()
                self.btnReject.Disable()
                #self._statusBar.SetFields(('',))
        
        def onTimer(self, event) :
                show = 'Sended %d, Received %d, Buffered %d' % self.talkManager.getStatusInfo()
                self._statusBar.SetFields((show,))
                
        def OnIconfiy(self, event):
                self.Hide()
                self.taskBarIcon.ShowIcon(True)
                
        def OnClose(self, event):
                #print "begin closeing"
                self.talkManager.stopManager() 
                #print "closeing 1"
                self.sessionManager.stopManager()
                #print "closeing 2"
                self.groupManager.stopManager()                
                #print "closeing 3"
                self.taskBarIcon.Destroy()
                self.Destroy()        
                #print "end closeing"
                
class EasyTalkApp(wx.App):
        def OnInit(self):
                wx.InitAllImageHandlers()
 
                self._mainFrame = MainFrame(None, -1)
                self.SetTopWindow(self._mainFrame)
      
                self._mainFrame.Show(True)
        
                return True
                
# end of class FriendsApp

if __name__ == "__main__":
	#try:
	scriptPath = os.path.dirname(__file__)
	os.chdir(scriptPath)
	#except:		
	#	pass

	app = EasyTalkApp(0)
        reactor.registerWxApp(app)
        reactor.run()
       
