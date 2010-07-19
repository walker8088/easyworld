
import os, os.path, logging, base64, datetime, time, random, stat, wx
import libxml2

from pyxmpp.iq     import Iq
from pyxmpp.utils  import to_utf8,from_utf8
from pyxmpp.stanza import Stanza, gen_id
from pyxmpp.interface  import implements
from pyxmpp.interfaces import *
from pyxmpp.utils      import from_utf8, to_utf8
from pyxmpp.xmlextra   import get_node_ns_uri
from pyxmpp.jabber.dataforms import * 

# ############################################################    
class FileTransferPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.count = 0

        wx.StaticText(self, -1, "This example shows the wx.Gauge control.", (45, 15))

        self.g1 = wx.Gauge(self, -1, 50, (110, 50), (250, 25))
        self.g2 = wx.Gauge(self, -1, 50, (110, 95), (250, 25))

        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
        self.timer.Start(100)

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        self.count = self.count + 1

        if self.count >= 50:
            self.count = 0

        self.g1.SetValue(self.count)
        self.g2.Pulse()
    
# ############################################################    

class FileTransferSession :
	def __init__(self, manager, jid, to_jid, file_path, file_name, transfer) :
		self.manager = manager
		
		self.sid = 0
		
		self.file_path = file_path
		self.file_name = file_name 
		self.file_size = 0
		
		self.transfer = transfer
		
		self.jid    = jid
		self.to_jid = to_jid
		
		self.file   = None
		self.seq    = -1
		self.pos    = None
		self.transfered_size = 0
		
		self.block_size = 4096
	        
		self.monitor = None 
		
		self.is_send = None
		
		self.status = "init" 
		
	def __str__(self) :	
		return '%s-%s' % (self.to_jid.bare().as_unicode(), self.sid)
	
	def get_progress(self) :
		if self.file_size == 0 :
			return 0
		return 100 * self.transfered_size / self.file_size
		
# ############################################################  

class FileSendSession(FileTransferSession) :
	def __init__(self, manager, jid, to_jid, file_path, file_name) :
		FileTransferSession.__init__(self, manager, jid, to_jid, file_path, file_name, None)
		
		self.sid = manager.new_sid()
		
		self.is_send = True
		
		fileStats = os.stat(os.path.join(file_path, file_name))

		fileInfo = { 
			'Size'         : fileStats [ stat.ST_SIZE ],
			'LastModified' : time.ctime ( fileStats [ stat.ST_MTIME ] ),
			'LastAccessed' : time.ctime ( fileStats [ stat.ST_ATIME ] ),
			'CreationTime' : time.ctime ( fileStats [ stat.ST_CTIME ] ),
			'Mode'         : fileStats [ stat.ST_MODE ]
			}
		self.file_size = fileInfo['Size']
	
        def open_request(self) :
		self.transfer.send_open_request(self) 
		self.status = "si_send_wait" 
		
	def close_request(self) :
		self.transfer.send_close_request(self)
			
	def open_success(self, transfer) :
		print "open success"
		self.seq = -1
		self.transfered_size = 0
		self.file = open(self.file_name, 'rb')
		self.status = 'sending'
		self.send_next(transfer)
	
	def send_next(self, transfer) :
		self.seq += 1	
		if self.seq > 65535 :
			self.seq = 0	
		data = self.file.read(self.block_size)	
		if len(data) > 0 :
			#print "send data : ", len(data)
			transfer.send_data_request(self, data)
			self.transfered_size += len(data) 
			if self.monitor :
				self.monitor.on_progress(self, 100 * self.transfered_size / self.file_size)
		else :
			print "close session"
			self.file.close()
			self.file = None
			self.status = "close" 
			self.close_request()
			self.monitor.on_close(self)
			
	def open_error(self) :
		#print "open error"
		if self.monitor :
			self.monitor.on_error(self, "open error")
		#self.manager.remove_session(self)
		self.status = 'si_open_error'
		
	def send_error(self) :
		#print "send error"
		#self.manager.remove_session(self)
		if self.monitor :
			self.monitor.on_error(self, "send error")
		
		self.status = 'send_error'
		
# ############################################################  

class FileReceiveSession(FileTransferSession) :
	def __init__(self, manager, sid, jid, to_jid, file_path, file_name, file_size, transfer) :
		FileTransferSession.__init__(self, manager, jid, to_jid, file_path, file_name, transfer)
		self.sid = sid
		self.file_size = file_size
		self.status = 'wait_accept'

	def send_si_response(self, accepted) :
		self.manager.send_si_response(self, accepted)
		
	def received_open(self) :
		file = os.path.join(self.file_path, self.file_name)
		#print "session open  : ", file
		self.file = open(file, "wb")
		self.seq = -1
		self.transfered_size = 0
		self.status = 'receiving'
		#print datetime.datetime.now() 
		return True
	
	def received_data(self, data, seq) :
		#print "session received  : ", len(data)
		self.file.write(data)
		self.transfered_size += len(data) 
		if self.monitor :
			self.monitor.on_progress(self, 100 * self.transfered_size / self.file_size)
		self.seq = seq
		return True
		
	def received_close(self) :
		#print "session closed"
		#print datetime.datetime.now() 
		if self.file :
			self.file.close()
			self.file = None
			if self.monitor :
				self.monitor.on_close(self)
		
		self.status = 'close'
		
# ############################################################  
IM_FILE_TRANSFER_EVENT = wx.NewEventType()
EVT_IM_FILE_TRANSFER   = wx.PyEventBinder(IM_FILE_TRANSFER_EVENT, 1)  

class FileTransferEvent(wx.PyCommandEvent):
    def __init__(self, evtSrc, session, request, stanza = None):
        wx.PyCommandEvent.__init__(self, IM_FILE_TRANSFER_EVENT , id = -1)
        self.evtSrc  = evtSrc
	self.session = session
	self.request = request
        self.stanza  = stanza
        
# ############################################################  

SI_NS            = 'http://jabber.org/protocol/si'
FILE_TRANSFER_NS = 'http://jabber.org/protocol/si/profile/file-transfer'
FEATURE_NS       = 'http://jabber.org/protocol/feature-neg'
		
class FileTransferManager(object) :
	
	implements(IIqHandlersProvider)

	def __init__(self, client, save_folder):
		self.client = client
		self.save_folder = save_folder
		
		self.ibb = IBB(client, self)
		
		self.sessions = {}
		
	#---------------------------------------------------------------------------------------------------------------------------------#
        def new_send_session(self, to_jid, file_name) :
		file_info = os.path.split(file_name) 
		session = FileSendSession(self, self.client.jid, to_jid, file_info[0], file_info[1])
		return session
		
	def send_si_request(self, session) :
		'''
		<iq type='set' id='offer1' to='receiver@jabber.org/resource'>
			<si xmlns='http://jabber.org/protocol/si' id='a0' mime-type='text/plain' profile='http://jabber.org/protocol/si/profile/file-transfer'>
			<file xmlns='http://jabber.org/protocol/si/profile/file-transfer' name='test.txt' size='1022' hash='552da749930852c69ae5d2141d3766b1' date='1969-07-21T02:56:15Z'>
			<desc>This is a test. If this were a real file...</desc>
			</file>
			<feature xmlns='http://jabber.org/protocol/feature-neg'>
			<x xmlns='jabber:x:data' type='form'>
			<field var='stream-method' type='list-single'>
			<option><value>>>http://jabber.org/protocol/bytestreams</value></option>
			<option><value>>>http://jabber.org/protocol/ibb</value></option>
			</field>
			</x>
			</feature>
			</si>
		</iq>
		'''
		
		stream = self.client.get_stream()
		
		#new_id = stream.generate_id()
		iq = Iq(None, session.jid, session.to_jid, "set", session.sid)
		si_node = iq.add_new_content(SI_NS, 'si')
		si_node.setProp("id", session.sid)
		si_node.setProp("mime-type", 'application/octet-stream')
		si_node.setProp("profile", FILE_TRANSFER_NS)
	
		file_node = si_node.newChild(None,"file",None)
		file_node.setProp("xmlns", FILE_TRANSFER_NS)
		file_node.setProp("name", to_utf8(session.file_name))
		file_node.setProp("size", to_utf8(session.file_size))
	
		feature_node = si_node.newChild(None, "feature", None)
		feature_node.setProp("xmlns", FEATURE_NS)
        
		form = Form()
		form.add_field( name = 'stream-method', field_type = 'list-single', 
                        #options = [Option('http://jabber.org/protocol/bytestreams', None), Option('http://jabber.org/protocol/ibb', None)])
			options = [Option('http://jabber.org/protocol/ibb', None)])
		form.as_xml(feature_node)
		stream.set_response_handlers(iq, self.received_si_success, self.received_si_error)
		stream.send(iq)
		
		self.sessions[session.sid] = session
		
	def received_si_success(self, stanza) :
		id = stanza.get_id()
		session = self.sessions[id]
		session.transfer = self.ibb
		#session.transfer = self.socks5
		session.open_request()
			
	def received_si_error(self, stanza) :
		id = stanza.get_id()
		del self.sessions[id]	
		
	#---------------------------------------------------------------------------------------------------------------------------------#
        
	def received_si_request(self, stanza) :
		'''
		should response :
		<iq type='result' to='sender@jabber.org/resource' id='offer1'>
			<si xmlns='http://jabber.org/protocol/si'>
			<file xmlns='http://jabber.org/protocol/si/profile/file-transfer'/>
			<feature xmlns='http://jabber.org/protocol/feature-neg'>
				<x xmlns='jabber:x:data' type='submit'>
					<field var='stream-method'>
						<value>http://jabber.org/protocol/bytestreams</value>
					</field>
				</x>
			</feature>
			</si>
		</iq>
		'''
		from_jid = stanza.get_from()
		sinode = stanza.get_query()
		sid = from_utf8(sinode.prop('id'))
		node = sinode.children
		while node :
			if node.ns() :
				ns = get_node_ns_uri(node)
				if  ns == FILE_TRANSFER_NS :
					filenode = node
				elif ns == FEATURE_NS :
					featurenode = node
			node = node.next
		
		filename = from_utf8(filenode.prop('name'))
		filesize = int(filenode.prop('size'))
		
		session = FileReceiveSession(self, sid, self.client.jid, from_jid, self.save_folder, filename, filesize, self.ibb)
		session.stanza = stanza.copy()
		self.sessions[str(session)] = session
		
		evt = FileTransferEvent(self, session, 'open')
		self.client.evtHandler.ProcessEvent(evt)
        
	def send_si_response(self, session, accepted) : 	
		stanza = session.stanza
		session.stanza = None
		if accepted :
			iq = stanza.make_result_response()
			si_node = iq.add_new_content(SI_NS, 'si')
			
			file_node = si_node.newChild(None,"file",None)
			file_node.setProp("xmlns", FILE_TRANSFER_NS)
			
			feature_node = si_node.newChild(None, "feature", None)
			feature_node.setProp("xmlns", FEATURE_NS)
	        
			form = Form('submit')
			form.add_field(name = 'stream-method',  
	                        options = [Option(session.transfer.NS, None)]) 
				#options = [Option('http://jabber.org/protocol/ibb', None)])
			form.as_xml(feature_node)
		else :
			iq = stanza.make_error_response('not-acceptable')
		
		self.client.get_stream().send(iq)
		#print iq.serialize()
		
	#---------------------------------------------------------------------------------------------------------------------------------#
        
	def get_iq_set_handlers(self):
		return [
			("si", "http://jabber.org/protocol/si", self.received_si_request)
		]

	def get_iq_get_handlers(self):
		return []
	
	#---------------------------------------------------------------------------------------------------------------------------------#
        def get_session(self, to_jid, sid) :
		if sid in self.sessions :
			return self.sessions[sid]
		key = '%s-%s' % (to_jid.bare().as_unicode(), sid)
		if key in self.sessions :
			return self.sessions[key]
		else :
			return None
			
	def remove_session(self, session) :
		key = str(session)
		if key in self.sessions :
			del self.sessions[key]
		else :
			print "error in remove session : ", key
			
	def new_sid(self) :
		return "send-%i" % (time.time(),)
		
# ############################################################       
IBB_NS = 'http://jabber.org/protocol/ibb'

class IBB(object) :

	implements(IIqHandlersProvider)

	def __init__(self, client, manager):
		self.NS = IBB_NS
		self.client = client
		self.session_mgr = manager
		
		self.init_sessions = {}
		self.active_sessions = {}
	#---------------------------------------------------------------------------------------------------------------------------------#
        
	def send_open_request(self, session) :
		'''
		<iq type='set' 
		    from='romeo@montague.net/orchard'
		    to='juliet@capulet.com/balcony'
		    id='inband_1'>
		  <open sid='mySID' 
		        block-size='4096'
		        xmlns='http://jabber.org/protocol/ibb'/>
		</iq>
		'''

		stream = self.client.get_stream()
		new_id = stream.generate_id()
		iq = Iq(None, session.jid, session.to_jid, "set", new_id)
	        node = iq.add_new_content(IBB_NS, 'open')
		node.setProp('sid', session.sid)
		node.setProp('block-size', str(session.block_size))
		stream.set_response_handlers(iq, self.received_open_success, self.received_open_error)
	        stream.send(iq)
		
		self.init_sessions[new_id] = session
		
	def received_open_success(self, stanza) :
		'''
		<iq type='result' 
		    from='juliet@capulet.com/balcony'
		    to='romeo@montague.net/orchard'
		    id='inband_1'/>
		'''
		from_jid = stanza.get_from()
		id = stanza.get_id()
		if id not in self.init_sessions :
			return
                session = self.init_sessions.pop(id)
		session.open_success(self)
		
	def received_open_error(self, stanza) :
		'''
		<iq type='error' 
		    from='juliet@capulet.com/balcony'
		    to='romeo@montague.net/orchard'
		    id='inband_1'/>
		    <error code='501' type='cancel'>
		         <feature-not-implemented xmlns='urn:ietf:params:xml:ns:xmpp-stanzas'/>
		    </error>
		</iq>
		'''
		from_jid = stanza.get_from()
		id = stanza.get_id()
		if id not in self.init_sessions :
			return
                session = self.init_sessions[id]
		session = self.init_sessions.pop(id)
		session.open_error()
		
	def send_close_request(self, session) :
		'''
		<iq type='set' 
		    from='romeo@montague.net/orchard'
		    to='juliet@capulet.com/balcony'
		    id='inband_2'>
		  <close xmlns='http://jabber.org/protocol/ibb' sid='mySID'/>
		</iq>
		'''
		stream = self.client.get_stream()
		new_id = stream.generate_id()
		iq = Iq(None, session.jid, session.to_jid, "set", new_id)
	        node = iq.add_new_content(IBB_NS, 'close')
		node.setProp('sid', session.sid)
		stream.set_response_handlers(iq, self.received_close_success, self.received_close_error)
	        stream.send(iq)
		self.active_sessions[new_id] = session
		
	def received_close_success(self, stanza) :
		#print stanza.serialize()
		from_jid = stanza.get_from()
		id = stanza.get_id()
		session = self.active_sessions.pop(id)
		#session.close()
		
	def received_close_error(self, stanza) :
		print stanza.serialize()
		
	def send_data_request(self, session, data) :
		'''
		<iq from='romeo@montague.net/orchard' to='juliet@capulet.com/balcony' type='set' id='ibb1'>
		  <data xmlns='http://jabber.org/protocol/ibb' sid='mySID' seq='0'>
		    qANQR1DBwU4DX7jmYZnncmUQB/9KuKBddzQH+tZ1ZywKK0yHKnq57kWq+RFtQdCJ
		    WpdWpR0uQsuJe7+vh3NWn59/gTc5MDlX8dS9p0ovStmNcyLhxVgmqS8ZKhsblVeu
		    IpQ0JgavABqibJolc3BKrVtVV1igKiX/N7Pi8RtY1K18toaMDhdEfhBRzO/XB0+P
		    AQhYlRjNacGcslkhXqNjK5Va4tuOAPy2n1Q8UUrHbUd0g+xJ9Bm0G0LZXyvCWyKH
		    kuNEHFQiLuCY6Iv0myq6iX6tjuHehZlFSh80b5BVV9tNLwNR5Eqz1klxMhoghJOA
		  </data>
		</iq>
		'''
		stream = self.client.get_stream()
		new_id = stream.generate_id()
		iq = Iq(None, session.jid, session.to_jid, "set", new_id)
	        node = iq.add_new_content(IBB_NS, 'data')
		node.setProp('sid', session.sid)
		node.setProp('seq', str(session.seq))
		node.setContent(base64.b64encode(data))
		stream.set_response_handlers(iq, self.received_data_success, self.received_data_error)
	        stream.send(iq)
		self.active_sessions[new_id] = session
		
	def received_data_success(self, stanza) :
		#print stanza.serialize()
		sid = stanza.get_id()
		print 'send_data_successed :', sid
		from_jid = stanza.get_from()
		session = self.active_sessions.pop(sid)
		#session = self.session_mgr.get_session(from_jid, sid)
		session.send_next(self)
		
	def received_data_error(self, stanza) :
		#print stanza.serialize()
		print 'send_data_error'
		from_jid = stanza.get_from()
		sid = stanza.get_id()
		session = self.active_sessions.pop(sid)
		#session = self.session_mgr.get_session(from_jid, sid)
		session.send_error()
		
	#---------------------------------------------------------------------------------------------------------------------------------#
        
	def received_open_request(self, stanza) :
		from_jid = stanza.get_from()
		sid = from_utf8(stanza.get_query().prop('sid'))
		print "open sid:", sid
		session = self.session_mgr.get_session(from_jid, sid) 
		if session :
			session.received_open()
			iq = stanza.make_result_response()
		else :
			iq = stanza.make_error_response('unexpected-request')
		self.client.get_stream().send(iq)
	
	def received_close_request(self, stanza) :
		from_jid = stanza.get_from()
		sid = from_utf8(stanza.get_query().prop('sid'))
		session = self.session_mgr.get_session(from_jid, sid) 
		if session :
			session.received_close()
			iq = stanza.make_result_response()
		else :
			iq = stanza.make_error_response('unexpected-request')
		self.client.get_stream().send(iq)
	
	def received_data(self, stanza) :
		from_jid = stanza.get_from()
		iq = stanza.get_query()
		sid  = from_utf8(iq.prop('sid'))
		data = base64.b64decode(iq.getContent())
		seq  = from_utf8(iq.prop('seq'))
		print "get data seq : ", seq
		session = self.session_mgr.get_session(from_jid, sid) 
		if session :
			session.received_data(data, seq)
			iq = stanza.make_result_response()
		else :
			iq = stanza.make_error_response('unexpected-request')
		self.client.get_stream().send(iq)
	
	#---------------------------------------------------------------------------------------------------------------------------------#
    
	def get_iq_set_handlers(self):
		return [
			("open",  IBB_NS, self.received_open_request),
			("close", IBB_NS, self.received_close_request),
			("data",  IBB_NS, self.received_data),
		]

	def get_iq_get_handlers(self):
		return []
	
# ############################################################    
class SocksStreamHandler(object):
	implements(IIqHandlersProvider, IFeaturesProvider)
	
	def __init__(self, client):
		"""Just remember who created this."""
		self.client = client

	def get_features(self):
		"""Return namespace which should the client include in its reply to a
		disco#info query."""
		return ["http://jabber.org/protocol/bytestreams"]

	def get_iq_get_handlers(self):
		"""Return list of tuples (element_name, namespace, handler) describing
		handlers of <iq type='get'/> stanzas"""
		return [
			("query", "http://jabber.org/protocol/bytestreams", self.get_version),
			]

	def get_iq_set_handlers(self):
		"""Return empty list, as this class provides no <iq type='set'/> stanza handler."""
		return []

# ############################################################    

