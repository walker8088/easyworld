
#coding:utf-8

import os, sys, os.path, string
import utils

from pyExcelerator import *

class CountInfo :
	def __init__(self, fileName, fileType = '', lineCount = 0, commentLineCount = 0, blankLineCount = 0, byteCount = 0) :
		self.fileName = fileName
                self.fileType = fileType
		self.fileCount = 0
		self.lineCount = lineCount
		self.commentLineCount  = commentLineCount
		self.blankLineCount  = blankLineCount
		self.byteCount = byteCount
		
class LineCounter :
	COUNTER_TYPE = None
	
	def __init__(self, manager):
		self.manager = manager
		if self.COUNTER_TYPE :
			self.manager.registerLineCounter(self.COUNTER_TYPE, self)
		
	def doCount(self, fileName) :			 
		info = CountInfo(fileName)
                info.fileType = self.COUNTER_TYPE
		self.isInAnnotation = False
		
		file = open(info.fileName)
		lines = file.readlines()
		file.close()
		
		for line in lines :
			sline = line.strip()
			if sline == '' :
				info.blankLineCount += 1	
			elif self.isCommentLine(sline) :
				info.commentLineCount += 1
			else :
				info.lineCount += 1

		info.byteCount += os.path.getsize(fileName)
		return info
	
	def isCommentLineCppStyle(self, line) :
		if not self.isInAnnotation :
			if line.startswith("//") :
				return True
			elif line.startswith("/*") and line.endswith("*/") :
				return True
			elif line.startswith("/*") :
				self.isInAnnotation = True
				return True
			else :
				return False
		else :
			if line.endswith("*/") :
				self.isInAnnotation = False
			return True
			
class TextLineCounter(LineCounter):
	COUNTER_TYPE = 'text'
	
	def isCommentLine(self, line) :
		return False
                
class SqlLineCounter(LineCounter):
	COUNTER_TYPE = 'sql'
	
	def isCommentLine(self, line) :
		return False

class XmlLineCounter(LineCounter):
	COUNTER_TYPE = 'xml'
	
	def isCommentLine(self, line) :
		return False

class HtmlLineCounter(LineCounter):
	COUNTER_TYPE = 'html'
	
	def isCommentLine(self, line) :
		return False

class JspLineCounter(LineCounter):
	COUNTER_TYPE = 'jsp'
	
	def isCommentLine(self, line) :
		return False

class CppLineCounter(LineCounter):
	COUNTER_TYPE = 'cpp'
	
	def __init__(self, manager) :
		LineCounter.__init__(self, manager)
		self.isCommentLine = self.isCommentLineCppStyle
				
class JavaLineCounter(CppLineCounter):
	COUNTER_TYPE = 'java'

class JavaScriptLineCounter(CppLineCounter):
	COUNTER_TYPE = 'javascript'

class CSharpLineCounter(CppLineCounter):
	COUNTER_TYPE = 'c#'

class PythonLineCounter(LineCounter):
	COUNTER_TYPE = 'python'
	
	def isCommentLine(self, line) :
		if not self.isInAnnotation :
			if line.startswith("#") :
				return True
			elif line.startswith("'''") and line.endswith("'''"):
				return True
			elif line.startswith('"""') and line.endswith('"""'):
				return True	
			elif line.startswith("'''") or line.startswith('"""'):
				self.isInAnnotation = True
				self.expectStopAnnotation = line[:3]
				return True
			else :
				return False
		else :
			if line.endswith(self.expectStopAnnotation) :
				self.isInAnnotation = False
			return True
	
ignores = (".doc", ".docx", ".xls", '.ppt', '.mpp', '.pdf', 
           ".db", ".dbf", 
           '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.ico', 'icon', '.swf', 
           '.svn-base', 
           '.jar', '.class', 
           '.rar', '.zip', '.7z', 
           '.resx', '.csproj', '.obj', '.bak', '.jude',
           '.txt',
           )

class CountManager :
	def __init__(self) :
		self.fsTypeDict = {}
		self.fsTypeDict['.sql'] = 'sql'
		self.fsTypeDict['.xml'] = 'xml'
		self.fsTypeDict['.jsp'] = 'jsp'
		self.fsTypeDict['.wml'] = 'html'
		self.fsTypeDict['.htm'] = 'html'
		self.fsTypeDict['.html'] = 'html'
		self.fsTypeDict['.js'] = 'javascript'
		self.fsTypeDict['.cs'] = 'c#'
		self.fsTypeDict['.java'] = 'java'
		self.fsTypeDict['.cpp'] = 'cpp'
		self.fsTypeDict['.c'] = 'cpp'
		self.fsTypeDict['.h'] = 'cpp'
		self.fsTypeDict['.hpp'] = 'cpp'
		self.fsTypeDict['.py'] = 'python'
		self.fsTypeDict['.pyw'] = 'python'
		self.fsTypeDict['.tac'] = 'python'
		
		self.countInfoDict = {}
		
		self.countDict = {}
		self.counters = []
		self.counters.append(CppLineCounter(self))
                self.counters.append(JavaLineCounter(self))
                self.counters.append(JavaScriptLineCounter(self))
		self.counters.append(PythonLineCounter(self))
		self.counters.append(SqlLineCounter(self))
		self.counters.append(JspLineCounter(self))
		self.counters.append(HtmlLineCounter(self))
		self.counters.append(XmlLineCounter(self))
                
                self.countInfoList = []
		self.TotalCountInfo = CountInfo("Total")
		
	def registerLineCounter(self, type, counter) :
		self.countDict[type] = counter
		for key in self.fsTypeDict.keys() :
			if self.fsTypeDict[key] == type :
				self.fsTypeDict[key] = counter
				
	def getCounter(self, extension) :
		if extension in self.fsTypeDict :
			return self.fsTypeDict[extension]
		else:
			return None
			
	def appendCountInfo(self, info) :
		(any , ext) = os.path.splitext(info.fileName)
		extension = ext.lower()
                
                if info.fileType in self.countInfoDict :
                        currCountInfo = self.countInfoDict[info.fileType]           
                else :
			currCountInfo = CountInfo(extension, info.fileType)
			self.countInfoDict[info.fileType] = currCountInfo 
		
		currCountInfo.fileCount += 1
		currCountInfo.lineCount += info.lineCount	
		currCountInfo.commentLineCount += info.commentLineCount
		currCountInfo.blankLineCount += info.blankLineCount
		currCountInfo.byteCount += info.byteCount
		
		self.TotalCountInfo.fileCount += 1	
		self.TotalCountInfo.lineCount += info.lineCount	
		self.TotalCountInfo.commentLineCount += info.commentLineCount
		self.TotalCountInfo.blankLineCount += info.blankLineCount
		self.TotalCountInfo.byteCount += info.byteCount	
		self.countInfoList.append(info)
	
        def countFolder(self, folder) :
                for root, dirs, files in os.walk(folder):
                        for file_name in files:
                                (any , ext) = os.path.splitext(file_name)
                                extension = ext.lower().strip()
                                if extension == '':
                                        continue
                                counter = self.getCounter(extension)
                                if not counter :
                                        continue
                                '''
                                if not counter :
                                        if (extension  not in ignores) and (extension not in errors):
                                                errors.append(extension)
                                        continue
                                '''
                                relatedpath = utils.relpath(root, folder)  
                                real_file = os.path.join(relatedpath, file_name)
                                info = counter.doCount(real_file)
                                self.appendCountInfo(info)
		
	def dispCountInfo(self) :
		print "-------------------------------------------------------------------------------"
                print "%-8s  %-8s  %-8s  %-8s  %-8s   %-8s   %-8s" % \
                            ("Type", "Files", "Code", "Comment", "Comment/Code", "Blank", "Bytes/Line")
                print "-------------------------------------------------------------------------------"
                for key in self.countInfoDict :
			countInfo = self.countInfoDict[key]
                        if countInfo.lineCount > 0 :
                                commentRate = (100 * float(countInfo.commentLineCount) / (countInfo.lineCount + countInfo.commentLineCount))
                        else :
                                commentRate = 0.0
			print "%-8s  %-8d  %-8d  %-8d  %-4.1f %%         %-8d   %.1f" % \
                                (countInfo.fileName, countInfo.fileCount, 
                                countInfo.lineCount, countInfo.commentLineCount,
                                commentRate,
                                countInfo.blankLineCount,
                                float(countInfo.byteCount) / (countInfo.lineCount + 
                                        countInfo.commentLineCount + countInfo.blankLineCount))
                print "-------------------------------------------------------------------------------"
                if self.TotalCountInfo.lineCount > 0 :
                        commentRate = (100 * float(self.TotalCountInfo.commentLineCount) / self.TotalCountInfo.lineCount)
                else :
                        commentRate = 0.0
                print "%-8s  %-8d  %-8d  %-8d  %-4.1f %%         %-8d   %.1f" % \
                                ("Total", self.TotalCountInfo.fileCount, 
                                self.TotalCountInfo.lineCount, self.TotalCountInfo.commentLineCount,
                                commentRate,
                                self.TotalCountInfo.blankLineCount,
                                float(self.TotalCountInfo.byteCount) / (self.TotalCountInfo.lineCount + self.TotalCountInfo.commentLineCount 
                                        + self.TotalCountInfo.blankLineCount))

        def writeReportFile(self, fileName) :
                fstyle = XFStyle()
                fstyle.num_format_str = '0.0%'
                
                w = Workbook()
                
                ws2 = w.add_sheet(u"按分类统计")
                row = 1
                ws2.write(row, 1, u"类别")
                ws2.write(row, 2, u"文件数")
                ws2.write(row, 3, u"有效行")
                ws2.write(row, 4, u"代码行")
                ws2.write(row, 5, u"注释行")
                ws2.write(row, 6, u"空行")
                ws2.write(row, 7, u"注释率")
                
                row += 1
                for key in self.countInfoDict :
                        info = self.countInfoDict[key]
                        ws2.write(row, 1, info.fileType)
                        ws2.write(row, 2, info.fileCount)
                        ws2.write(row, 3, info.lineCount + info.commentLineCount)
                        ws2.write(row, 4, info.lineCount)
                        ws2.write(row, 5, info.commentLineCount )
                        ws2.write(row, 6, info.blankLineCount )
                        ws2.write(row, 7, Formula('F%d/D%d' % (row + 1, row + 1)), fstyle)
                        row += 1
                ws2.write(row, 1, u"总计" )
                ws2.write(row, 2, Formula('SUM(C3:C%d)' % (row)))
                ws2.write(row, 3, Formula('SUM(D3:D%d)' % (row)))
                ws2.write(row, 4, Formula('SUM(E3:E%d)' % (row)))
                ws2.write(row, 5, Formula('SUM(F3:F%d)' % (row)))
                ws2.write(row, 6, Formula('SUM(C3:C%d)' % (row)))
                ws2.write(row, 7, Formula('F%d/D%d' % (row + 1, row + 1)), fstyle)
                
                ws = w.add_sheet(u"按文件统计")
                ws.write(1, 1, u"目录")
                ws.write(1, 2, u"文件名")
                ws.write(1, 3, u"类别")
                ws.write(1, 4, u"有效行")
                ws.write(1, 5, u"代码行")
                ws.write(1, 6, u"注释行")
                ws.write(1, 7, u"空行")
                ws.write(1, 8, u"注释率")
                ws.write(1, 9, u"作者")
                
                row = 2
                lastfolder = ''
                for info in self.countInfoList :
                        folder, file = os.path.split(info.fileName)
                        if folder != lastfolder :
                                ws.write(row, 1, folder )
                                lastfolder = folder        
                        ws.write(row, 2, file )
                        ws.write(row, 3, info.fileType)
                        ws.write(row, 4, info.lineCount + info.commentLineCount)
                        ws.write(row, 5, info.lineCount)
                        ws.write(row, 6, info.commentLineCount )
                        ws.write(row, 7, info.blankLineCount )
                        ws.write(row, 8, Formula('G%d/E%d' % (row + 1, row + 1)), fstyle)
                        row += 1
                ws.write(row, 1, u"总计" )
                ws.write(row, 4, Formula('SUM(E3:E%d)' % (row)))
                ws.write(row, 5, Formula('SUM(F3:F%d)' % (row)))
                ws.write(row, 6, Formula('SUM(G3:G%d)' % (row)))
                ws.write(row, 7, Formula('SUM(H3:H%d)' % (row)))
                ws.write(row, 8, Formula('G%d/E%d' % (row + 1, row + 1)), fstyle)
                
                w.save(fileName)
                
if __name__ == "__main__":		
	if len(sys.argv) == 1 :
		folder = os.getcwd() 
	elif len(sys.argv) == 2 :
		folder = sys.argv[1] 
        mgr = CountManager()
	mgr.countFolder(folder)
        mgr.dispCountInfo()
        