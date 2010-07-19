
import os, os.path, config, string, base64

from Crypto.Cipher import AES

from configobj import ConfigObj

        
import wx

__doc__="""
Holds global data.

"""
            
# ############################################################
class GlobalConfig :
	def __init__(self) :
		self.storages   = {}
		self.engineDict = {}

		self.defImages  = {}
		self.defBitmaps = {}
		self.defIcons   = {}
		self.imclient   = None
		self.online = False

		self.auto_reconnect  = True
		
		# Xml resources
		self.res    = None
		self.config = None
	
	def on_online(self) :
		self.online = True
		for name in self.storages :
			storage = self.storages[name]
			storage.storage_mgr = self.imclient.storage_mgr
			storage.load()
			
	def on_offline(self) :
		self.online = False
		for name in self.storages :
			storage = self.storages[name]
			storage.unload()
		
	def register_storage(self, sitem) :
		self.storages[sitem.name] = sitem
		
	def load_config(self, congfig_file) :
		self.config = ConfigObj(congfig_file)
		try :
			Account = self.config['Account']
		except :
			self.config['Account'] = {
				'userid'   : '[YoutName]@jabber.org', 
				'password' : '',
				'server'   : 'None'
			} 
			
		try :
			ChatOption = self.config['Chat']
		except :
			self.config['Chat'] = {'messge_crypt' : 'none', 'save_folder' : "received_files" } # ''private', none' or ''
		
		save_folder = self.config['Chat']['save_folder']
		
		if not os.path.exists(save_folder) or not os.path.isdir(save_folder) :
			os.mkdir(save_folder)
		
		try :
			sysOption = self.config['System']
		except :
			self.config['System'] = {'debug' : 'no', } # 'none' or ''
	
	def save_config(self) :
		self.config.write()
		
	def setUserAccount(self, user_id, password, server) :
		self.config['Account']['userid'] = user_id
		self.config['Account']['password'] = self.encode(password)
		if server :
			self.config['Account']['server'] = server
		else :
			self.config['Account']['server'] = 'None'
		
	def getUserAccount(self) :
		Account = self.config['Account']
		if Account['server'] == 'None' :
			server = None
		else :
			server = Account['server']
			
		return ( Account['userid'], self.decode(Account['password']),  server)
	
	def textEncode(self, text) :
		if self.config['Chat']['messge_crypt'] == 'private' :
			dtext = base64.b64encode(text.encode('utf-8'))
			return dtext.swapcase()
		else :
			return text
                
	def textDecode(self, text) :
		if self.config['Chat']['messge_crypt'] == 'private' :
			ctext = base64.b64decode(text.swapcase())
			return ctext.decode('utf-8')
		else :
			return text
	
	def getIcon(self, bitmap):
		icon = wx.EmptyIcon()
		icon.CopyFromBitmap(bitmap)
		return icon

	def getBitmap(self, name):
		#global defImages, defBitmaps, defIcons 
		#print name
		if name not in self.defImages.keys() :
			self.defImages[name] = wx.Image(os.path.join('res', name + '.png'), wx.BITMAP_TYPE_PNG)   
			#print name
		return wx.BitmapFromImage(self.defImages[name])

	def encode(self, message) :
	        obj=AES.new('test keytest key', AES.MODE_ECB)
	        to16 = 16 - len(message) % 16
	        dtext = message + to16 * ' '
	        ciphertext=obj.encrypt(dtext)
	        return base64.b64encode(ciphertext)

	def decode(self, message) :
	        try :
			ctext = base64.b64decode(message)
			obj2 = AES.new('test keytest key', AES.MODE_ECB)
			dtext = obj2.decrypt(ctext)
			return string.strip(dtext)
		except :
			return message

# ############################################################
	
glob = GlobalConfig()

# ############################################################



 	 	