
#coding:utf-8

from datetime import *
from LineCounter import *
	
if len(sys.argv) == 1 :
	folder = os.getcwd() 
elif len(sys.argv) == 2 :
	folder = sys.argv[1] 

mgr = CountManager()
mgr.countFolder(folder)
mgr.writeReportFile(u"代码统计报告-%s.xls" % datetime.now().strftime("%Y%m%d-%H%M") )
