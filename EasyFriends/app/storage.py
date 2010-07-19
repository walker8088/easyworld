
from pyxmpp.iq         import Iq
from pyxmpp.utils      import from_utf8,to_utf8
from pyxmpp.interface  import implements
from pyxmpp.interfaces import *

# ############################################################       
class StorageItemMonitor :
	def on_load(self, isok) :
		pass
	
	def on_save(self, isok) :
		pass
	
	def on_unload(self) :
		pass
		
class StorageItem(object) :
	def __init__(self, name_space, name, storage_mgr = None) :
		self.storage_mgr = storage_mgr
		self.name_space  = name_space
		self.name   = name
		self.status = 'unlink'
		self.monitor = None
		
	def load(self) :
		self.status = 'waiting_load'
		self.storage_mgr.query_get(self.name_space, self.name, self)
		
	def save(self) :
		self.status = 'waiting_save'
		self.storage_mgr.query_set(self.name_space, self.name, self.to_xml(), self)
	
	def unload(self) :
		self.storage_mgr = None
		self.status = 'unlink'
		if self.monitor :
			self.monitor.on_unload()
			
	def set_monitor(self, monitor) :
		self.monitor = monitor
	
	def on_load_result(self, data) :
		self.from_xml(data)
		self.status = 'ok'
                if self.monitor :
			self.monitor.on_load(True)
		
	def on_load_error(self) :
		self.status = 'error_load'
		if self.monitor :
			self.monitor.on_load(False)
		
	def on_save_result(self, isok) :
		if isok :
			self.status = 'ok'
                else :	
			self.status = 'error_save'
		if self.monitor :
			self.monitor.on_save(isok)
		
	def to_xml(self) :
		pass
	
	def from_xml(self, xml) :
		pass
		
# ############################################################       
class StorageManager(object) :
	def __init__(self, client):
		self.client = client
		self.handlers = {}
			
	def query_get(self, ns = None, element = None, handler = None) :
		stream = self.client.get_stream()
		new_id = stream.generate_id()
		
		iq = Iq(None, None, None, "get", new_id)
	        node = iq.new_query('jabber:iq:private')
		if element :
			enode = node.newChild(None,to_utf8(element),None)
			if ns:
				ns=enode.newNs(ns,None)
				enode.setNs(ns)
			#
		#	
	        if handler :
			self.handlers[new_id] = handler
		stream.set_response_handlers(iq, self.on_get_result, self.on_get_error)
	        stream.send(iq)
		
	def query_set(self, ns, element, data, handler = None) :
		stream = self.client.get_stream()
		new_id = stream.generate_id()
		iq = Iq(None, None, None, "set", new_id)
	        node = iq.new_query('jabber:iq:private')
		enode = node.newChild(None,to_utf8(element),None)
		ns=enode.newNs(ns,None)
		enode.setNs(ns)
		enode.addContent(data)
	        stream.set_response_handlers(iq, self.on_set_result, self.on_set_error)
	        stream.send(iq)
		if handler :
			self.handlers[new_id] = handler
		
	def on_get_result(self, stanza) :
		q=stanza.get_query()
		c = q.children
		str = c.getContent()
		id = stanza.get_id()
		if id in self.handlers :
			handler = self.handlers[id]
			handler.on_load_result(str)
			del self.handlers[id]
		else :
			print "error in received_get_data"
		#print str.decode('utf-8')
		
		#evt = IMEvent(self, IM_PRIVATE_DATA_EVENT, str)
		#self.client.evtHandler.ProcessEvent(evt)
		#print stanza.serialize()
	
	def on_get_error(self, stanza) :
		id = stanza.get_id()
		if id in self.handlers :
			handler = self.handlers[id]
			handler.on_load_error()
			del self.handlers[id]
		else :
			print "error in received_get_error"
			
	def on_set_result(self, stanza) :
		#evt = ResultEvent(self, True)
		#self.client.evtHandler.ProcessEvent(evt)
		id = stanza.get_id()
		if id in self.handlers :
			handler = self.handlers[id]
			handler.on_save_result(True)
			del self.handlers[id]
		else :
			print "error in received_set_success"
		
	def on_set_error(self, stanza) :
		#evt = ResultEvent(self, False)
		#self.client.evtHandler.ProcessEvent(evt)
		id = stanza.get_id()
		if id in self.handlers :
			handler = self.handlers[id]
			handler.on_save_result(False)
			del self.handlers[id]
		else :
			print "error in received_set_error"
		
# ############################################################       
     
