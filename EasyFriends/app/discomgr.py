
from pyxmpp.iq         import Iq
from pyxmpp.utils      import from_utf8,to_utf8
from pyxmpp.interface  import implements
from pyxmpp.interfaces import *

class DiscoManager(object) :
	
	implements(IFeaturesProvider)

	def __init__(self, client) :
		self.client = client
	
	def get_features(self):
		"""Return namespace which should the client include in its reply to a
		disco#info query."""
		return ["jubatu:games"]

	def query_get_server(self) :
		stream = self.client.get_stream()
		discoIq = Iq(None, self.client.jid, self.client.jid.domain, "get", stream.generate_id())
		discoIq.new_query('http://jabber.org/protocol/disco#info')
		stream.set_response_handlers(discoIq, self.on_get_result, self.on_get_error)
		stream.send(discoIq)
	
	def query_get(self, jid, handler) :
		stream = self.client.get_stream()
		iq = Iq(to_jid=jid, stanza_type="get")
		q=iq.new_query(VCARD_NS, "vCard")
		stream.set_response_handlers(iq, self.on_get_result, self.on_get_error)
		stream.send(iq)
		self.handler = handler
		
	def query_set(self, vcard) :
		stream = self.client.get_stream()
		new_id = stream.generate_id()
		iq = Iq(None, None, None, "set", new_id)
	        node=iq.new_query(VCARD_NS, "vCard")
		vcard.as_xml(node)
		stream.set_response_handlers(iq, self.on_set_result, self.on_set_error)
		stream.send(iq)
			
	def on_get_result(self, stanza) :
		try:
			node=stanza.get_query()
			if node:
				vcard=VCard(node)
			else:
				vcard=None
	        except (ValueError,),e:
			vcard=None
	        if vcard is None:
			#self.error(u"Invalid vCard received from "+stanza.get_from().as_unicode())
			return
	        else :
			"""TODO"""
			self.handler.on_vcard(vcard)
			
	
	def on_get_error(self, stanza):
	        err=stanza.get_error()
		#print stanza.serialize()
	        #self.error(u"vCard query error from %s: %s" % (stanza.get_from(),err.get_message()))
		
		#evt = IMEvent(self, IM_VCARD_EVENT, stanza)
		#evt.result = False
	        #self.evtHandler.ProcessEvent(evt)
	
	#---------------------------------------------------------------------------------------------------------------------------------#
    
	def received_disco_info(self, stanza):
	        """Handle the receipt of disco#info information."""
	        #print stanza.serialize()
	        logging.getLogger("xmppComm").debug(stanza.serialize())
	        di = DiscoInfo(stanza.get_query())
	        if di.has_feature("jubatu:games"):
	            logging.getLogger("xmppComm").debug("'jubatu:games' feature detected")
	            discoIq = pyxmpp.iq.Iq(None, self.jid, stanza.get_from(), "get", self.get_stream().generate_id())
	            xmlNode = discoIq.new_query('http://jabber.org/protocol/disco#items')
	            xmlNode.setProp("node", "jubatu-engines")
	            self.get_stream().set_response_handlers(discoIq, self.received_disco_items, self.iq_error)
	            self.get_stream().send(discoIq)
	            
	def received_disco_items(self, stanza):
	        """Handle the receipt of disco#items information."""
	        
	        logging.getLogger("xmppComm").debug(stanza.serialize())
	        discoItems = DiscoItems(stanza.get_query())
	        
	        engineCollection = set()
	        for item in discoItems.get_items():
	            engineCollection.add(item.get_node().split('/')[-1])
	            
	        logging.getLogger("xmppComm").debug("Engine IDs: %s", engineCollection)
	        #self.AddPendingEvent(events.JuEngineList(stanza.get_from_jid(), engineCollection))
	
	def disco_get_my_info(self, client, node, iq):
	        
		"""Return disco#info.
	        
	        Besides the basic configuration, it's added the identity for jubatu and the feature "jubatu:games"
	        """
	        
	        logging.getLogger("xmppComm").debug("Request stanza:\n%s", iq.serialize())
	        di = JabberClient.disco_get_info(self, node, iq)
	            
	        if node=="jubatu-engines":
	            if di is None:
	                di = DiscoInfo("jubatu-engines")  # we mirror the node in accordance with XEP-0030 3.2
	                
	        logging.getLogger("xmppComm").debug("Returned Disco#info:\n%s", di.xmlnode.serialize())
	        return di

	def disco_get_my_items(self, client, node, iq):
	        """Return disco#items.
	        
	        When the items for the jubatu-game-list node are required, we construct it. Otherwise, the basic info is
	        returned.
	        """
	        
	        logging.getLogger("xmppComm").debug("Request stanza:\n%s", iq.serialize())
	        logging.getLogger("xmppComm").debug("Node queried: %s", node)
	        
	        if node is None:
	            discoItems = JabberClient.disco_get_items(self, node, iq)
	            discoItems.add_item(self.jid, "jubatu-engines")
	        elif node=="jubatu-engines":
	            discoItems = DiscoItems()
	            for engine in glob.engineDict.values():
	                discoItems.add_item(self.jid, "jubatu-engines/"+engine.id())
	        else:
	            discoItems = JabberClient.disco_get_items(self, node, iq)
	            
	        logging.getLogger("xmppComm").debug("Returned disco#items:\n%s", discoItems.xmlnode.serialize())
	        return discoItems
			