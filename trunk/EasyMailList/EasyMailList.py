#!/usr/bin/python
#
# This script is a helper to clean POP3 mailboxes
# containing malformed mails that hangs MUA's, that 
# are too large, or whatever...
#
# It iterates over the non-retrieved mails, prints
# selected elements from the headers and prompt the 
# user to delete bogus messages.
#
# Written by Xavier Defrang <xavier.defrang@brutele.be>
# 
# 
import xlrd
import poplib, smtplib, re
import time, os, os.path, shutil
import logging,string,datetime
import mimetypes
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

class MailListItem :
	def __init__(self) :
		self.setList("");
		#self.setPopAccount("pop.com", "inspurworld-bu4@com", "******")
		#self.setSmtpAccount("smtp.com")
		
	def setPopAccount(self, host, user, passwd) :
		self.popHost   = host
		self.popUser   = user
		self.popPasswd = passwd
		
	def setSmtpAccount(self, host, user = None, passwd = None) :
		self.smtpHost   = host
		
		if user != None :
			self.smtpUser = user
		else :
			self.smtpUser = self.popUser
		
		if passwd != None :
			self.smtpPasswd = passwd
		else :
			self.smtpPasswd = self.popPasswd
			
	def setList(self, name, groupMembers = None, listMembers = None) :
		self.name = name
		
		if groupMembers != None :
			self.groupMembers = groupMembers[:]
		else : 
			self.groupMembers = list()
			
		if listMembers != None :
			self.listMembers = listMembers[:]
		else :
			self.listMembers = list()
		
	
#end class MailListItem

class MailListBot :
	""" """
	
	def __init__(self, isDaemon) :
		self.configFileTime = 0
		if isDaemon :
			self.workFolder =  "/var/maillistbot/"
		else :
			self.workFolder =  os.getcwdu()
			
		self.logFile = os.path.join(self.workFolder,"maillistbot.log")
		self.configFile = os.path.join(self.workFolder, "SanyoProjMailList.xls")
		self.spamMsgFolder = os.path.join(self.workFolder, "SPAM_OR_BAD_MESSAGE")
		
	def checkListFolders(self) :
		logging.info("Checking mailbox msg folders......")
		for item in self.mailList :
			folder = os.path.join(self.workFolder, item.name)
			if not os.path.isdir(folder) :
				try :
					os.makedirs(folder)
					logging.info("Created mailbox msg folder : %s ", folder)
				except OSError :
					logging.info("Error in creating mailbox msg folder : %s ", folder)
					return False;		
					
		if not os.path.isdir(self.spamMsgFolder) :
			try :
				os.makedirs(self.spamMsgFolder)
				logging.info("Created error msg folder : %s ", self.spamMsgFolder)
			except OSError :
				logging.info("Error in creating error msg folder : %s ", self.spamMsgFolder)
				return False;
		logging.info("Checked OK.")
		return True
		
	def loadMailListFromConfigFile(self) :
		""" """
		
		self.mailList = []
		
		logging.info("Loading MailList form config File : %s", self.configFile)
		
		book = xlrd.open_workbook(self.configFile)
		
		logging.info("File Opened. Processing......")
		
		sheet = book.sheet_by_index(0)
		
		#print sheet.name, sheet.nrows, sheet.ncols
		#print "Cell D30 is", sheet.cell_value(rowx=29, colx=3)
		currGroup = ""
		currSubGroups = []
		currMembers = []	
		for row in range(4, sheet.nrows):
			groupValue = sheet.cell_value(row, 1)
			
			if currGroup == "" : 
				if groupValue != "" : # find first group
					currGroup = groupValue
					logging.debug("Find a new group : %s at line : %d", groupValue, row + 1)	
					subGroupValue = sheet.cell_value(row, 3)
					if subGroupValue != "" :
						logging.debug("Find a new subgroup : %s at line %d", subGroupValue, row + 1)
						currSubGroups.append(subGroupValue)
					memberValue = sheet.cell_value(row, 5)
					if memberValue != "" :
						logging.debug("Find a new member : %s at line %d", memberValue, row + 1)
						currMembers.append(memberValue + "@com")					
				else :	
					logging.error("Can't find main group name in the line %d", row + 1)
			else :
				if groupValue != "" : 
					logging.debug("Find a new group : %s at line : %d", groupValue, row + 1)
					# find a new group. add current group to MailList
					listItem = MailListItem()
					listItem.setPopAccount("pop.com", currGroup + "@com", "****")
					listItem.setSmtpAccount("smtp.com", currGroup + "@com", "****")
					
					listItem.setList(currGroup, currSubGroups, currMembers)
					self.mailList.append(listItem)
					
					#new group is made. subgroup and mb\embers belong to new group
					currGroup = groupValue
					currSubGroups = []
					currMembers = []
					
				subGroupValue = sheet.cell_value(row, 3)
				if subGroupValue != "" :
					logging.debug("Find a new subgroup : %s at line %d", subGroupValue, row + 1)
					currSubGroups.append(subGroupValue)
				memberValue = sheet.cell_value(row, 5)
				if memberValue != "" :
					logging.debug("Find a new member : %s at line %d", memberValue, row + 1)
					currMembers.append(memberValue + "@com")
					
		
		#After reading the last line. add the last grouop to MailList
		if currGroup != "" :
			listItem = MailListItem()
			listItem.setList(currGroup, currSubGroups, currMembers)
			listItem.setPopAccount("pop.com", currGroup + "@com", "******")
			listItem.setSmtpAccount("smtp.com", currGroup + "@com", "******")
			self.mailList.append(listItem)	
		
		logging.info("Process end. List groups here:")
		
		for item in self.mailList :
			logging.info("GroupName : %s", item.name)
			logging.info("SubGroups : %s", item.groupMembers)
			logging.info("Members   : %s", item.listMembers)

		statinfo = os.stat(self.configFile)
		self.configFileTime = statinfo.st_mtime 
				
		if self.checkListFolders() :
			return True
		else :
			return False
			
	def configFileChanged(self) :
		""" """
		statinfo = os.stat(self.configFile)
		if self.configFileTime == statinfo.st_mtime :
			return False
		else :
			return True

	def loadMessageFromFile(self, msgFile) :
		""" """
		try :
			f = open(msgFile, "rb")
		except IOError :
			logging.error("Can't open file %s",  msgFile)
			return None
			
		try :		
			msgs = f.read()
			#for msg in msgs :
			#	print msg
		except IOError :
			logging.error("Can't read file %s",  msgFile)
			msgs = None
		finally :	
			f.close()	
		
		return msgs
			
	def writeMessageToFile(self, folder, fileName, itemLines) :
		""" """
		msgFile = os.path.join(folder, fileName)
		try :
			f = open(msgFile,"wb+")
		except IOError :
			logging.error("Error in open file : %s", msgFile) 
			return False
		try :		
			for line in itemLines :
				f.write(line + "\r\n")
			result = True
			logging.info("Writed msg to file : %s ", msgFile) 
		except IOError :	
			logging.error("Error in writing to file : %s", msgFile) 
			result = False
		finally :	
			f.close()	
			
		return result
		
	def processPopMail(self, mailListItem) :
		logging.info("Poping mail : %s",  mailListItem.popUser)
		rx_headers  = re.compile(r"^(From)")
		try:
			# Connect to the POPer and identify user
			pop = poplib.POP3(mailListItem.popHost)
			
			pop.user(mailListItem.popUser)
			pop.pass_(mailListItem.popPasswd)

			# Get some general informations (msg_count, box_size)
			stat = pop.stat()
			logging.info("Total %d message(s)", stat[0])

			bye = 0
			count_del = 0
			for n in range(stat[0]):
				msgnum = n + 1

				# Retrieve headers
				response, lines, bytes = pop.retr(msgnum) #pop.top(msgnum, MAXLINES)
				
				#TODO : Check spam mails here
				headlines = lines[0:15]
				matchFrom = filter(rx_headers.match, headlines)
				findError = False
				
				msgFile   = str(msgnum)
				msgFolder = os.path.join(self.workFolder, mailListItem.name)
				
				for matchLine in matchFrom :
					if string.lower(matchLine) == "from: mailer-daemon@mail.com" :
						logging.error("Find a mealer-daemon return back mail, saving it to SPAM folder.")
						msgFolder = self.spamMsgFolder	
						msgFile = datetime.datetime.now().isoformat()
						break;
						
				if not self.writeMessageToFile(msgFolder, msgFile, lines) :
					logging.error("Can't write %d msg to file : %s. processing next msg.", msgnum, )
					continue
				
				# Print message info and headers we're interrested in
				logging.info( "Message %d (%d bytes)" % (msgnum, bytes))
				logging.info( "-" * 30)
				logging.info( "\n".join(filter(rx_headers.match, headlines)))
				logging.info( "-" * 30)
				
				pop.dele(msgnum)
				
			# Commit operations and disconnect from server
			pop.quit()
			
		#except poplib.error_proto, detail:
		except :
			# Fancy error handling
			logging.error("POP3 Protocol Error: ")
		#finally :
			
	def processSendMail(self, mailListItem) :
		""" """
		logging.info("Sending mail : %s",  mailListItem.smtpUser)

		listFolder = os.path.join(self.workFolder, mailListItem.name)
		fileList = os.listdir(listFolder)
		logging.info("Total %d file(s)",  len(fileList))
		for fileName in  fileList:
			msgFile = os.path.join(listFolder, fileName)
			logging.info("Sending message file: %s", msgFile)
			if os.path.isdir(msgFile) :
				logging.error("Find a folder: %s. Skip it.", msgFile)
				continue
				
			#copy message file to subgroups and rename it	
			for folder in mailListItem.groupMembers :
				destFile = os.path.join(self.workFolder, folder, mailListItem.name + "." + fileName)
				logging.info("Copying file %s --> %s", msgFile, destFile)
				shutil.copy2(msgFile, destFile) 

			#List Members are not  empty			
			if len(mailListItem.listMembers) > 0 :
				message = self.loadMessageFromFile(msgFile)
				if message == None :
					logging.error("Can't load file : %s.", msgFile)	
				else :	
					try:
						#logging.info("Sending mail to : %s",  mailListItem.listMembers)
						smtp = smtplib.SMTP(mailListItem.smtpHost)
						#smtp.set_debuglevel(2)
						#smpt.login(mailListItem.smtpUser, mailListItem.smtpPasswd)
						if not g_SmtpDryRun :
							smtp.sendmail(mailListItem.smtpUser, mailListItem.listMembers, message)
						smtp.quit()
						logging.info("Sended mail to : %s",  mailListItem.listMembers)
					except :
						logging.error("SMTP Error in sending mail to : %s", mailListItem.listMembers)
			
			os.remove(msgFile)
				
	def runBot(self) :
		logging.basicConfig(level = logging.DEBUG,
			format = '%(asctime)s %(levelname)-8s %(message)s', datefmt = '%a, %d %b %Y %H:%M:%S', filename = self.logFile, filemode = 'w')

		
		if not self.loadMailListFromConfigFile() :
			logging.error("Loading config file error, exited.")
			return False
		
		running = True
		while running :
			print "Working..."
			logging.info("Working...")
			if self.configFileChanged() :
				if not self.loadMailListFromConfigFile() :
					logging.error("Loading config file error, please check the config file or work directory.")
			for item in self.mailList :	
				self.processSendMail(item)
			for item in self.mailList :
				self.processPopMail(item)
			for item in self.mailList :
				self.processSendMail(item)
			
			print "Sleeping..."
			logging.info("Sleeping...")
			
			time.sleep(60*5)
			#running = False
		return True;
		
#end class MailListBot

global g_SmtpDryRun #if SmtpDryRun  =  true then not send mail to smtp server  

g_SmtpDryRun = False

bot = MailListBot(isDaemon = True)
bot.runBot()
