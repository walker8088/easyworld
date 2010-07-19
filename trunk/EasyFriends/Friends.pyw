#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, logging, traceback

LOG_FILE = 'friends.log'

try:
        import psyco
        psyco.profile()
except ImportError:
        pass

from ctypes import c_int, WINFUNCTYPE, windll  
from ctypes.wintypes import HWND, LPCSTR, UINT  
prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)  
paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", None), (1, "flags", 0)  
MessageBox = prototype(("MessageBoxA", windll.user32), paramflags)  

scriptPath = os.path.split(sys.argv[0])[0]
if scriptPath != '' :
	os.chdir(scriptPath)

logging.basicConfig(level = logging.INFO,
			format = '%(asctime)s  %(levelname)s  %(message)s',
			filename = LOG_FILE, filemode = 'w+')

try :				
	from app import app
	app = app.Application(False)
	app.RunApp()
except :
	errInfo = traceback.format_exc()
	for info in errInfo.split("\n") :
		logging.error(info)
	MessageBox(text=u"对不起，程序出了点小问题，不能运行啦！\n\n请把%s文件发给作者walker li先生，他会立即帮您解决的.\n" % LOG_FILE, 
			caption="Friends Application") 

	