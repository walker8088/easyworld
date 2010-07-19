import os, logging, md5, asyncore, socket
import wx


# ############################################################    
class SocketConnection(asyncore.dispatcher):
	def __init__(self, parent, socket, RECV_BUFFER_LEN = 4096):
		asyncore.dispatcher.__init__(self, socket)
		self.parent = parent
		self.RECV_BUFFER_LEN = RECV_BUFFER_LEN
		self.SendData = ""
		
		
	def handle_read(self):
		data = self.recv(self.RECV_BUFFER_LEN)
		if len(self.RecvData) > 0:
			self.parent.onReceived(self, data)
	
	def handle_write(self):
		send_byte = self.send(self.SendData)
		if send_byte > 0:
			send_out = self.SendData[:send_byte]
			self.SendData = self.SendData[send_byte:]
			self.handle_write()
		else:
			self.SendData = ""

	def writable(self):
		return False
  
	def handle_close(self):
		self.parent.onConnectionLost(self, '')
		self.close()
       
# ############################################################    
class TcpServer(asyncore.dispatcher):
	def __init__(self, port):
		asyncore.dispatcher.__init__(self)
		self.port = port
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
	
	def start(self) :	
		self.bind(('', self.port))
		self.listen(5)
		
	def stop(self) :
		self.socket.close()
		
	# -------------------------------------------------------------------------------------------------------------------- #	
	def onConnectionMade(self, con) :
		pass
		
	def onConnectionLost(self, con, reason) :
		pass
		
	def onReceived(self, con, data) :
		pass	
	# -------------------------------------------------------------------------------------------------------------------- #	
		
	def handle_accept(self):
		clientSocket, address = self.accept()
		con = SocketConnection(self, clientSocket)
		self.onConnectionMade(con)
		
	def handle_connect(self):
		pass

			
# ############################################################   		
class TcpClient(asyncore.dispatcher):

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_read(self):
        data = self.recv(8192)
	self.OnRead(data)
	
    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

 
# ############################################################                
class MessageHint(wx.Dialog) :
        def __init__(self, parent, title = '', 
                size=(600, 600), pos=wx.DefaultPosition, style = wx.STAY_ON_TOP ) : # wx.DEFAULT_DIALOG_STYLE ) :
                
                pre = wx.PreDialog()
                #pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
                pre.Create(parent, -1, title, pos, size, style)

                self.PostCreate(pre)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
                
		self.label = wx.StaticText(self, -1, '')
		sizer.Add(self.label, 1, wx.ALIGN_TOP | wx.ALL | wx.EXPAND, 5)
		
		self.timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.OnTimer)
		
		self.SetSizer(sizer)
		self.Fit()
		
        def Msg(self, msg) :
		self.label.SetLabel(msg)
		self.Fit()
		self.CenterOnParent()
		self.timer.Start(600, False)
                self.ShowModal()
		
	def OnTimer(self, event) :
		self.timer.Stop()
		self.EndModal(0)
# ############################################################                

def file_hash(file):
    """Return a hash of the content of a file (encoded as a hex string)."""
    
    hash = md5.new()
    fb = open(file, 'rb')
    readBytes = 4192;
    while (readBytes):
        readString = fb.read(readBytes);
        hash.update(readString);
        readBytes = len(readString);
    fb.close()
    
    return hash.hexdigest()

def get_preferred_languages():
    """Return the preferred languages according with user's settings."""
    
    userLang = wx.GetApp().userData.get('configuration', 'language').split(',')
    
    if (len(userLang) == 0):
        return ['es']
    else:
        return userLang
    
def get_user_data_path():
    "Convenience function to get the full path for the user specific data file."
    
    return os.path.join(get_user_dir(), 'userdata')

def get_user_dir():
    """Return the directory used to store the user specific data. (Selected language, etc.)"""
    
    configPath = os.path.join(os.path.expanduser("~"), ".jubatu")
    logging.getLogger("core").debug("User data dir: %s", configPath)
    return configPath

def get_game_dirs():
    """Return a list with the root directories for game modules.
    
    A couple of directories can hold the game modules: the directorie where the main jubatu module
    is located, and a user-dependent one (located in whatever place the OS use to locate user's profiles).
    """
    
    dirList = []
    path = os.path.join(os.getcwdu(), "games")
    logging.getLogger("core").debug("Path #1: %s", path)
    if os.path.exists(path):
        dirList.append(path)
    path = os.path.join(get_user_dir(), "games")
    logging.getLogger("core").debug("Path #2: %s", path)
    if os.path.exists(path):
        dirList.append(path)
    return dirList

def random_hex_string(numberOfBytes):
    """Return a random number formatted as a hex string.
    
    numberOfBytes -- number of random bytes asked (every byte will be formatted as a couple of hex digits)
    
    The implementation rely on os.urandom, which *should* be a reliable and criptografically secure
    random number generator. This will depend heavily on the OS, however.
    """
    
    aux = os.urandom(numberOfBytes)
    randomString = ""
    
    for i in range(numberOfBytes):
        randomString += hex(ord(aux[i]))[2:]
        
    return unicode(randomString)
    
  