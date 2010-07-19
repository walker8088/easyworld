
from pyxmpp.iq         import Iq
from pyxmpp.utils      import from_utf8,to_utf8
from pyxmpp.interface  import implements
from pyxmpp.interfaces import *

from pyxmpp.jabber.vcard import VCARD_NS, VCard

class VcardManager(object) :
	def __init__(self, client) :
		self.client = client
		
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
			
		'''
	        #self.cjc.set_user_info(stanza.get_from(),"vcard",vcard)
	        msg=u"vCard for %s:\n" % (stanza.get_from(),)
	        print msg
		
	        msg+=u" Full name:   %s\n" % (vcard.fn.value)
	        if vcard.n.given:
	            msg += u" Given name:  %s\n" % (vcard.n.given)
	        if vcard.n.middle:
	            msg += u" Middle name: %s\n" % (vcard.n.middle)
	        if vcard.n.family:
	            msg += u" Family name: %s\n" % (vcard.n.family)
	        for title in vcard.title:
	            msg += u" Title:       %s\n" % (title.value)
	        for role in vcard.role:
	            msg += u" Role:        %s\n" % (role.value)
	        for email in vcard.email:
	            if "internet" in email.type:
	                msg += u" E-Mail:      %s\n" % (email.address,)
	        for nick in vcard.nickname:
	            msg += u" Nick:        %s\n" % (nick.value,)
	        for photo in vcard.photo:
	            if photo.uri:
	                msg += u" Photo:       %s\n" % (photo.uri,)
	            else:
	                msg += u" Photo:       cannot display\n"
	        for logo in vcard.logo:
	            if logo.uri:
	                msg += u" Logo:        %s\n" % (logo.uri,)
	            else:
	                msg += u" Logo:        cannot display\n"
	        for bday in vcard.bday:
	            msg += u" Birthday:    %s\n" % (bday,)
	        for adr in vcard.adr:
	            msg += u" Address (%s):\n" % (u", ".join(adr.type),)
	            if adr.pobox:
	                msg += u"  PO Box:     %s\n" % (adr.pobox,)
	            if adr.extadr:
	                msg += u"              %s\n" % (adr.extadr,)
	            if adr.street:
	                msg += u"  Street:     %s\n" % (adr.street,)
	            if adr.locality:
	                msg += u"  Locality:   %s\n" % (adr.locality,)
	            if adr.region:
	                msg += u"  Region:     %s\n" % (adr.region,)
	            if adr.pcode:
	                msg += u"  Postal code: %s\n" % (adr.pcode,)
	            if adr.ctry:
	                msg += u"  Country:     %s\n" % (adr.ctry,)
	        for label in vcard.label:
	            msg += u" Address label (%s):\n" % (u", ".join(label.type),)
	            for l in label.lines:
	                msg += u"  %s\n" % (l,)
	        for tel in vcard.tel:
	            msg += u" Phone (%s):  %s\n" % (u", ".join(tel.type), tel.number)
	        for jabberid in vcard.jabberid:
	            msg += u" JID:         %s\n" % (jabberid.value,)
	        for mailer in vcard.mailer:
	            msg += u" Mailer:      %s\n" % (mailer.value,)
	        for tz in vcard.tz:
	            msg += u" Time zone:   %s\n" % (tz.value,)
	        for geo in vcard.geo:
	            msg += u" Geolocation: %s, %s\n" % (geo.lat, geo.lon)
	        for org in vcard.org:
	            msg += u" Organization: %s\n" % (org.name, )
	            if org.unit:
	                msg += u" Org. unit:   %s\n" % (org.unit, )
	        for categories in vcard.categories:
	            msg += u" Categories:  %s\n" % (u", ".join(categories.keywords),)
	        for note in vcard.note:
	            msg += u" Note:        %s\n" % (note.value,)
	        for sound in vcard.sound:
	            if sound.uri:
	                msg += u" Sound:       %s\n" % (sound.uri,)
	            else:
	                msg += u" Sound:       cannot play\n"
	        for uid in vcard.uid:
	            msg += u" User id:     %s\n" % (uid.value,)
	        for url in vcard.url:
	            msg += u" URL:         %s\n" % (url.value,)
	        for desc in vcard.desc:
	            msg += u" Description: %s\n" % (desc.value,)
	        print msg
	        #self.info(msg)
	        '''
	
	def on_get_error(self, stanza):
	        err=stanza.get_error()
		#print stanza.serialize()
	        #self.error(u"vCard query error from %s: %s" % (stanza.get_from(),err.get_message()))
		
		#evt = IMEvent(self, IM_VCARD_EVENT, stanza)
		#evt.result = False
	        #self.evtHandler.ProcessEvent(evt)
	
	def on_set_result(self, stanza) :
		print "vard set success"
		pass
	
	def on_set_error(self, stanza) :
		print "vard set error"
		pass
		
		