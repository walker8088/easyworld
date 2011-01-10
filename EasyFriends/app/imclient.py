#!/usr/bin/python -u
#
# This example is a simple "echo" bot
#
# After connecting to a jabber server it will echo messages, and accept any
# presence subscriptions. This bot has basic Disco support (implemented in
# pyxmpp.jabber.client.Client class) and jabber:iq:vesion.

import sys, socket, threading, logging, base64, datetime, time, random, os, stat 
import locale,codecs
import wx

import pyxmpp
from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.disco import *
from pyxmpp.jabber.client import JabberClient
from pyxmpp.jabber.vcard import VCARD_NS,VCard
from pyxmpp.jabber.register import Register

from pyxmpp.utils import from_utf8,to_utf8
from pyxmpp.xmlextra import get_node_ns_uri

#from pyxmpp.jabber.dataforms import * 

from pyxmpp.interface import implements
from pyxmpp.interfaces import *

from glob import glob
import discomgr, filemgr, storage, vcardmgr

# ############################################################      
#status changed
IM_STATUS_CHANGED_EVENT = wx.NewEventType()
EVT_IM_STATUS_CHANGED = wx.PyEventBinder(IM_STATUS_CHANGED_EVENT, 1)  

class IMStatusEvent(wx.PyCommandEvent):
    def __init__(self, eventSrc, state, arg):
        wx.PyCommandEvent.__init__(self, IM_STATUS_CHANGED_EVENT, id = -1)
        self.eventSrc = eventSrc
        self.state = state
        self.arg = arg

# ############################################################      
#RAW IO	
IM_RAW_IO_EVENT = wx.NewEventType()
EVT_IM_RAW_IO   = wx.PyEventBinder(IM_RAW_IO_EVENT, 1)  

class IMRawIOEvent(wx.PyCommandEvent):
    def __init__(self, evtSrc, IOType, Data):
        wx.PyCommandEvent.__init__(self, IM_RAW_IO_EVENT, id = -1)
        self.evtSrc = evtSrc
        self.IOType = IOType
        self.Data = Data

# ############################################################      
#connected
IM_CONNECTED_EVENT = wx.NewEventType()
EVT_IM_CONNECTED   = wx.PyEventBinder(IM_CONNECTED_EVENT, 1)  

#authenticated
IM_AUTHENTICATED_EVENT = wx.NewEventType()
EVT_IM_AUTHENTICATED   = wx.PyEventBinder(IM_AUTHENTICATED_EVENT, 1)  

#authorized
IM_AUTHORIZED_EVENT = wx.NewEventType()
EVT_IM_AUTHORIZED   = wx.PyEventBinder(IM_AUTHORIZED_EVENT, 1)  

#disconnected
IM_DISCONNECTED_EVENT = wx.NewEventType()
EVT_IM_DISCONNECTED   = wx.PyEventBinder(IM_DISCONNECTED_EVENT, 1)  

#presence update
IM_PRESENCE_UPDATE_EVENT = wx.NewEventType()
EVT_IM_PRESENCE_UPDATE   = wx.PyEventBinder(IM_PRESENCE_UPDATE_EVENT, 1)  

#roster update
IM_ROSTER_UPDATE_EVENT = wx.NewEventType()
EVT_IM_ROSTER_UPDATE   = wx.PyEventBinder(IM_ROSTER_UPDATE_EVENT, 1)  

#presence control 
IM_PRESENCE_CONTROL_EVENT = wx.NewEventType()
EVT_IM_PRESENCE_CONTROL   = wx.PyEventBinder(IM_PRESENCE_CONTROL_EVENT, 1)  

#message received
IM_MESSAGE_RECEIVED_EVENT = wx.NewEventType()
EVT_IM_MESSAGE_RECEIVED   = wx.PyEventBinder(IM_MESSAGE_RECEIVED_EVENT, 1)  

IM_REGISTER_EVENT = wx.NewEventType()
EVT_IM_REGISTER   = wx.PyEventBinder(IM_REGISTER_EVENT, 1)  

IM_VCARD_EVENT = wx.NewEventType()
EVT_IM_VCARD   = wx.PyEventBinder(IM_VCARD_EVENT, 1)  

# ############################################################  

class IMEvent(wx.PyCommandEvent):
    def __init__(self, evtSrc, evtType, stanza = None):
        wx.PyCommandEvent.__init__(self, evtType, id = -1)
        self.evtSrc = evtSrc
        self.stanza = stanza
        self.result = None

class IMRosterEvent(wx.PyCommandEvent):
    def __init__(self, evtSrc, evtType, rostItem = None):
        wx.PyCommandEvent.__init__(self, evtType, id = -1)
        self.evtSrc = evtSrc
        self.rosterItem = rostItem

# ############################################################      
class VersionHandler(object):
    """Provides handler for a version query.
    
    This class will answer version query and announce 'jabber:iq:version' namespace
    in the client's disco#info results."""
    
    implements(IIqHandlersProvider, IFeaturesProvider)

    def __init__(self, client):
        """Just remember who created this."""
        self.client = client

    def get_features(self):
        """Return namespace which should the client include in its reply to a
        disco#info query."""
        return ["jabber:iq:version"]

    def get_iq_get_handlers(self):
        """Return list of tuples (element_name, namespace, handler) describing
        handlers of <iq type='get'/> stanzas"""
        return [
            ("query", "jabber:iq:version", self.get_version),
            ]

    def get_iq_set_handlers(self):
        """Return empty list, as this class provides no <iq type='set'/> stanza handler."""
        return []

    def get_version(self,iq):
        """Handler for jabber:iq:version queries.

        jabber:iq:version queries are not supported directly by PyXMPP, so the
        XML node is accessed directly through the libxml2 API.  This should be
        used very carefully!"""
	
        iq=iq.make_result_response()
        q=iq.new_query("jabber:iq:version")
        q.newTextChild(q.ns(),"name","Friends Application")
        q.newTextChild(q.ns(),"version","0.2")
	
        return iq

# ############################################################    

IM_PRIVATE_DATA_EVENT = wx.NewEventType()
EVT_IM_PRIVATE_DATA   = wx.PyEventBinder(IM_PRIVATE_DATA_EVENT, 1)

IM_PRIVATE_RESULT_EVENT = wx.NewEventType()
EVT_IM_PRIVATE_RESULT   = wx.PyEventBinder(IM_PRIVATE_RESULT_EVENT, 1)

class ResultEvent(wx.PyCommandEvent):
    def __init__(self, evtSrc, success):
        wx.PyCommandEvent.__init__(self, IM_PRIVATE_RESULT_EVENT, id = -1)
        self.evtSrc = evtSrc
        self.success = success
	
# ############################################################    
class DataInHandler(logging.Handler):
    def __init__(self, parent):
        logging.Handler.__init__(self, level = logging.DEBUG)
	self.parent = parent
	
    def emit(self, record):
        data=record.args[0]
	evt = IMRawIOEvent(self.parent, 'IN', data)
        self.parent.evtHandler.AddPendingEvent(evt)
	#print "IN :", record.args[0]

class DataOutHandler(logging.Handler):
    def __init__(self, parent):
        logging.Handler.__init__(self, level = logging.DEBUG)
	self.parent = parent
	
    def emit(self, record):
        data = record.args[0]
        evt = IMRawIOEvent(self.parent, 'OUT', data)
        self.parent.evtHandler.AddPendingEvent(evt)
	#print "OUT :", record.args[0]

# ############################################################    
class IMConnection(wx.EvtHandler, JabberClient):

    implements(IMessageHandlersProvider, IPresenceHandlersProvider, IIqHandlersProvider)
    
    def __init__(self, parent):
        
        wx.EvtHandler.__init__(self)
        
	self.data_in_handler=DataInHandler(self)
	self.data_out_handler=DataOutHandler(self)
	logger = logging.getLogger("pyxmpp.Stream.in");
	logger.setLevel(logging.DEBUG)
	logger.addHandler(self.data_in_handler)
	logger = logging.getLogger("pyxmpp.Stream.out")
	logger.setLevel(logging.DEBUG)
	logger.addHandler(self.data_out_handler)

	self.keepalive = 30
	
	tls = pyxmpp.TLSSettings(require=True, verify_peer=False)
	
	JabberClient.__init__(self, None, None, 
                keepalive = self.keepalive, disco_name=u'Jubatu', disco_category=u'client', disco_type=u'gaming', tls_settings=tls, auth_methods=['sasl:PLAIN'])
        self.isDetached = False 
        
	self.disco_mgr = discomgr.DiscoManager(self)
        self.file_transfer_mgr = filemgr.FileTransferManager(self, glob.config['Chat']['save_folder'])
	self.storage_mgr = storage.StorageManager(self)
	self.vard_mgr = vcardmgr.VcardManager(self)
	
	self.interface_providers = [
            self,
	    VersionHandler(self),
            self.disco_mgr,
	    self.file_transfer_mgr,
	    self.file_transfer_mgr.ibb,
	    ]
	    
        self.parent = parent
        self.evtHandler = self.parent.GetEventHandler()
	
    #---------------------------------------------------------------------------------------------------------------------------------#
    def get_iq_get_handlers(self) :
        return []
    
    def get_iq_set_handlers(self) :
	return [] 
	
    def get_message_handlers(self):
        return [
            ("normal", self.message_received),
            ]

    def get_presence_handlers(self):
	return [(None, self.presence_update),
		("unavailable", self.presence_update),
		("subscribe", self.presence_control),
		("subscribed", self.presence_control),
		("unsubscribe", self.presence_control),
		("unsubscribed", self.presence_control),
	       ]   
    
    #---------------------------------------------------------------------------------------------------------------------------------#
    
    def setUserAccount(self, jidstr, password, resource = 'pyxmpp') :
	jid=JID(jidstr)
	self.jid=JID(jid.node, jid.domain, resource)
	self.password=password   
	if not self.server :
		host = socket.gethostbyname(jid.domain)
		self.setServer(host)
		
    def setServer(self, server, port = 0) :
	self.server=server
	if port != 0 :
		self.port=port
	else :
                self.port=5222
    
    def addRoster(self, jidstr, nickname, groupname) :
        jid = JID(jidstr)
        if nickname == '':
                nickname = None
        if groupname == '':
                group = ()
        else :
                group = (groupname,)
        
        try :
                item = self.roster[jid]
        except Exception, e:
                item = None
        
        if not item :        
                item = self.roster.add_item(jid, name=nickname, groups = group)
                iq=item.make_roster_push()
                self.stream.send(iq)
                self.sendSubscribe(jid, "")
        else :
                if item.groups :
                        if groupname != '':
                                item.goups.append(groupname)
                else :
                        if groupname != '':
                                item.goups = (groupname,)
                                
                iq=item.make_roster_push()
                self.stream.send(iq)
        
    def removeRoster(self, rosterItem) :
        item = self.roster.remove_item(rosterItem)
	iq=item.make_roster_push()
	self.stream.send(iq)
    
    def getRosterInfo(self, jid):
        #TODO:
        pass
        
    def sendPresence(self, showMsg) :   
        p=Presence(show=showMsg, from_jid = self.jid)
        self.stream.send(p)

    def sendSubscribe(self, to, msg):
        toJID = JID(to)
        p=Presence( to_jid = toJID,  from_jid = self.jid, stanza_type = 'subscribe', status = msg )
        self.stream.send(p)

    def sendUnsubscribe(self, to):
        toJID = JID(to)
        p=Presence(to_jid = toJID,   from_jid = self.jid, stanza_type = 'unsubscribe')
        self.stream.send(p)
        
    def sendChatMessage(self, to,body) :
        ctext = glob.textEncode(body)
        
        m = Message(
            to_jid = to,
            from_jid = self.jid,
            stanza_type = 'chat',
            subject='',
            body = ctext
            )
        self.stream.send(m)

    def sendMessage(self, to, type, subject, body) :
        m = Message(
            to_jid = to,
            from_jid = self.jid,
            stanza_type = type,
            subject = subject,
            body = body
            )
        self.stream.send(m)
    
    def renameRoster(self, jid, newName) :
        try :
                item=self.roster[jid]
	except:
		print u"You don't have %s in your roster List" % (jid.as_unicode(),)
		return
	item.name = newName
	iq=item.make_roster_push()
	self.stream.send(iq)

    def renameGroup(self, oldName, newName) :
        items = self.roster.get_items_by_group(oldName)
	for item in items:
		for index in range(len(item.groups)) :
                        if item.groups[index] == oldName :
                                item.groups[index] = newName
                iq=item.make_roster_push()
                self.stream.send(iq)
  
    def print_roster_item(self,item):
        if item.name:
            name=item.name
        else:
            name=u""
        print (u'%s "%s" subscription=%s groups=%s'
                % (unicode(item.jid), name, item.subscription,
                    u",".join(item.groups)) )
    
    #---------------------------------------------------------------------------------------------------------------------------------#
    
    def authenticated(self) :
        JabberClient.authenticated(self)
        evt = IMEvent(self, IM_AUTHENTICATED_EVENT)
        self.evtHandler.AddPendingEvent(evt)
        
    def authorized(self) :
        JabberClient.authorized(self)
        # ########################
	self.sendPresence(None)	
	self.request_roster()
        # ########################
	evt = IMEvent(self, IM_AUTHORIZED_EVENT)
        self.evtHandler.AddPendingEvent(evt)
        
    def connected(self) :
        JabberClient.connected(self)
        
        evt = IMEvent(self, IM_CONNECTED_EVENT)
        self.evtHandler.AddPendingEvent(evt)
           
    def disconnected(self) :
        JabberClient.disconnected(self)
        
        evt = IMEvent(self, IM_DISCONNECTED_EVENT)
        self.evtHandler.AddPendingEvent(evt)
        
    def message_received(self, message) :

	#messageCopy = message.copy()
	#chat_state = self.get_chat_state(message)
        #print chat_state
		
	evt = IMEvent(self, IM_MESSAGE_RECEIVED_EVENT, message)
        self.evtHandler.ProcessEvent(evt)
        return True
          
    def roster_updated(self, item = None) :
	
        if item != None:
                evt = IMRosterEvent(self, IM_ROSTER_UPDATE_EVENT, item)
        else:
                evt = IMRosterEvent(self, IM_ROSTER_UPDATE_EVENT)
                
        self.evtHandler.AddPendingEvent(evt)
    
    def stream_created(self,stream):
	JabberClient.stream_created(self,stream)
	#print 'stream created'
    
    def stream_closed(self,stream):
	JabberClient.stream_closed(self,stream)
	#print 'stream closed'
    
    def stream_state_changed(self,state,arg):
        JabberClient.stream_state_changed(self,state,arg)
	evt = IMStatusEvent(self, state, arg)
        self.evtHandler.ProcessEvent(evt)
        #print "stream state :", state
	#print 'stream state changed'
	
    def session_started(self):    
        JabberClient.session_started(self)

    #---------------------------------------------------------------------------------------------------------------------------------#
    
    def open_muc(self, muc_room):     # Experimental; do not use in engines.
        """Experimental. Do not use."""
        
        logging.getLogger("xmppComm").debug("Opening muc")
        room_manager = muc.MucRoomManager(self.get_stream())
        room_state = muc.MucRoomState(room_manager, self.jid, pyxmpp.JID(muc_room), muc.MucRoomHandler())
        room_manager.set_handlers()
        room_state.join()
   	
    
    #---------------------------------------------------------------------------------------------------------------------------------#
    
    def presence_update(self, presence) :
        """Handle the reception of a presence stanza."""
        #print 'presence_updated'
	#presenceCopy = presence.copy()
        evt = IMEvent(self, IM_PRESENCE_UPDATE_EVENT, presence)
        self.evtHandler.ProcessEvent(evt)
	
    def presence_control(self, stanza):
        msg=unicode(stanza.get_from())
        t=stanza.get_type()
        accept_yes = True
	if t=="subscribe":
                fromjid = stanza.get_from()
                msg+=u" has requested presence subscription."
                try :
                        item = self.roster[fromjid]
                        if item.ask :
                                accept_yes = True
                        #print "i got it"
                except Exception, e:
        		#print e
			data  = stanza.copy()
                        evt = IMEvent(self, IM_PRESENCE_CONTROL_EVENT, data)
        		self.evtHandler.AddPendingEvent(evt)
			return True
        		#if evt.result == 'accept' :
        		#	accept_yes = True
        		#else :
        		#	accept_yes = False
                        #endif        
                #endif                        
        elif t=="subscribed":
            msg+=u" has accepted our presence subscription request."
        elif t=="unsubscribe":
            msg+=u" has canceled his subscription of me."
        elif t=="unsubscribed":
            msg+=u" has canceled our subscription of his presence."
        
	if accept_yes :
		p=stanza.make_accept_response()
	else :
		p=stanza.make_deny_response()
	self.stream.send(p)
		
        print msg
        
        return True
            
    #---------------------------------------------------------------------------------------------------------------------------------#
    
    def registration_form_received(self, stanza):
        print "registration_form_received :", stanza.serialise()
	JabberClient.registration_form_received(self, stanza)
	print "registration_form_received_end"
    
    def registration_error(self, stanza):
        print 'register_error'
        
        evt = IMEvent(self, IM_REGISTER_EVENT)
        evt.stanza = stanza 
        evt.result = False
        self.evtHandler.AddPendingEvent(evt)
       
        err = stanza.get_error()
        ae = err.xpath_eval("e:*",{"e":"jabber:iq:auth:error"})
        if ae:
            ae = ae[0].name
        else:
            ae = err.get_condition().name
        self.__logger.error(u"Registration error: %s (%s)" % (err.get_message(), ae))
    
    def registration_success(self, stanza):
        evt = IMEvent(self, IM_REGISTER_EVENT)
        evt.stanza = stanza 
        evt.result = True
        self.evtHandler.AddPendingEvent(evt)
       
        self.__logger.info(u"Registration at %s successful." % (stanza.get_from(),))        
    
    #---------------------------------------------------------------------------------------------------------------------------------#
    
    def disco_get_info(self, node, iq):
        return self.disco_mgr.disco_get_my_info(self, node, iq)
	
    def disco_get_items(self, node, iq):
        return self.disco_mgr.disco_get_my_items(self, node, iq)
	
    #---------------------------------------------------------------------------------------------------------------------------------#
    
    def loop_iter(self, timeout=0.05):
        """Implements an iteration of the main loop of the client."""
        
        stream=self.get_stream()
        if not stream:
            return
        try:
                act=stream.loop_iter(timeout)
                if not act:
                        self.idle()  
	except pyxmpp.streamsasl.SASLAuthenticationFailed:
            logging.debug("SASLAuthenticationFailed error")
            self.state_changed.acquire()
            try:
                try:
                    stream.close()
                except:
                    pass
            finally:
                self.stream = None
                self.state_changed.notify()
                self.state_changed.release()
		evt = IMEvent(self, IM_DISCONNECTED_EVENT)
                self.evtHandler.ProcessEvent(evt)
                #self.AddPendingEvent(events.JuSASLAuthenticationFailed())
	except Exception, e:
		print "loop_iter error : ", e
                self.state_changed.acquire()
                try:
                        try:
                                stream.close()
                        except:
                                pass
                finally:
                        self.stream = None
                        self.state_changed.notify()
                        self.state_changed.release()
                        
                        evt = IMEvent(self, IM_DISCONNECTED_EVENT)
                        self.evtHandler.ProcessEvent(evt)
                        #self.AddPendingEvent(events.JuSASLAuthenticationFailed())	
# ############################################################            
'''
class XmppClientThread(threading.Thread):
    """Thread managing the xmpp protocol.
    
    Only an object for this class is expected to be used, and it will be accesible program-wide as it will be contained
    in the main application class instance (wx.GetApp().xmppThread). This thread will contain the instance of XmppClient
    managing the protocol and a commands queue used to asynchonously receive command from other parts of the program.
    """
    
    xmppClient = None
    commandsQueue = Queue.Queue()
    __commandsQueue = []
    
    def __init__(self):
        logging.getLogger("xmppComm").setLevel(logging.WARNING)   # set the logging verbosity for this module here
        threading.Thread.__init__(self)

    def run(self):
        """Main loop for the thread.LockType
        
        Basicly, it iterate the 'xmppClient' object, check and process the received commands, and check
        the exit conditions.
        """
        
        while True:
            self.preprocess_commands()
            if len(self.__commandsQueue)>0:
                self.process_command(self.__commandsQueue.pop(0))
            if self.xmppClient!=None:
                self.xmppClient.loop_iter(1)
            time.sleep(0.1)
            # Exit condition.
            # wx seems to be None sometimes when the main window have been closed, so we have to check whether wx is None
            if len(self.__commandsQueue)==0 and (wx is None or not wx.GetApp().GetTopWindow()):
                return

    def preprocess_commands(self):
        """Preprocess the command list.
        
        This is primarily intended to allow to cancel some previous actions; take into account that some
        actions asked to the module can take a good amount of second before being complete (i.e., a connection)
        so it's probably a good idea to see if, after such wait, the user have issued another order and subsequently
        cancelled it.
        """
        
        try:
            while True:
                command = self.commandsQueue.get_nowait()
                if command.id==commands.JU_XMPP_CANCEL_CONNECT:
                    if len(self.__commandsQueue)>0:
                        assert(self.__commandsQueue[-1].id==commands.JU_XMPP_CONNECT)
                        self.__commandsQueue.pop(0)
                    else:
                        self.__commandsQueue.append(command)
                else:
                    self.__commandsQueue.append(command)
        except Queue.Empty:
            pass

    def process_command(self, command):
        """Process a received command, calling the appropiate handlers."""
        
        if command.id==commands.JU_XMPP_INITIALIZE:
            self.xmppClient = XmppClient(
                command.jid,
                command.password,
                command.server)
        elif command.id==commands.JU_XMPP_CONNECT:
            try:
                self.xmppClient.connect()
            except dns.exception.Timeout:
                logging.getLogger("xmppComm").error("dns.exception.Timeout error")
                wx.GetApp().AddPendingEvent(events.JuStatusMessageEvent(_("Timeout problem"), 5000))
                wx.GetApp().AddPendingEvent(events.JuDnsTimeout())
            except dns.resolver.NXDOMAIN:
                wx.GetApp().AddPendingEvent(events.JuStatusMessageEvent(_("NXDOMAIN problem"), 5000))
                wx.GetApp().AddPendingEvent(events.JuDnsDXDOMAIN())
            except socket.error, msg:
                logging.getLogger("xmppComm").error("Socket error")
                wx.GetApp().AddPendingEvent(events.JuStatusMessageEvent(_("Socket problem"), 5000))
                wx.GetApp().AddPendingEvent(events.JuSocketError())
        elif command.id==commands.JU_XMPP_CANCEL_CONNECT:
            if self.xmppClient != None:
                self.xmppClient.disconnect()
                self.xmppClient = None
        elif command.id==commands.JU_XMPP_DISCONNECT:
            self.xmppClient.disconnect()
        elif command.id==commands.JU_XMPP_SET_PRESENCE:
            self.xmppClient.set_presence(command.show)
        elif command.id==commands.JU_XMPP_SEND_IQ_STANZA:
            self.xmppClient.send_iq_stanza(command.stanza, command.res_handler, command.err_handler, command.timeout_handler, command.timeout)
        elif command.id==commands.JU_XMPP_SEND_IQ_STANZA_REPLY:
            self.xmppClient.send_iq_stanza_reply(command.stanza)
        elif command.id==commands.JU_XMPP_OPEN_MUC:
            self.xmppClient.open_muc()
'''        
