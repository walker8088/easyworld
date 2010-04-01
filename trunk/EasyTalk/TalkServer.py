#!/usr/bin/python

import sys, threading, time, socket
import string, sets, struct, Queue

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.application.internet import MulticastServer
from twisted.internet import threads 
  
class Talker :
        LIVE_COUNT = 3
        
        def __init__(self, name, address) :
                self.name = name
                self.address = address
                self.active()
        
        def active(self) :
                self.leftLife = self.LIVE_COUNT
        
        def dead(self) :
                self.leftLife -= 1
                if self.leftLife <= 0 :
                        return True
                else :
                        return False
                                  
class GroupMemberManagerServer(DatagramProtocol):
        def __init__(self) :
                self.memberList = []
                self.connector = None
                
        def startManager(self, port) :
                try :
                        self.connector = reactor.listenUDP(port, self)  
                        #print self.connector.getHost()        
                        self.port = port
                        
                        self.livingThread = LoopingCall(self.living)
                        self.livingThread.start(10)
                        
                        return True
                except Exception, e :
                        print e
                        self.connector = None
                        return False
                        
        def stopManager(self) :
                if self.connector != None :
                        self.livingThread.stop()
                        self.connector.stopListening()
                        if self.group != None :
                                self.leaveGroup()  
                
        def findUser(self, name) :       
                for item in self.memberList :       
                        if item.name == name :
                                return item
                return None
                
        def living(self) :
                for item in self.memberList :       
                        if item.dead() :
                                self.memberList.remove(item)
                                self.notifyAll("easytalk leave %s" % (item.name), item.address)
                                print "Dead :", item.name
                                del item
                                
                               
        def notifyAll(self, datagram, address) :
                strSend = '%s:%s:%d' % (datagram, address[0], address[1])
                for item in self.memberList :
                        self.transport.write(strSend, item.address)

        def sendMemberList(self, address) :
                if len(self.memberList) == 0:
                        return
                str = 'easytalk members '
                for item in self.memberList :
                        str += " %s:%s:%d" % (item.name, item.address[0], item.address[1])
                self.transport.write(str, address)
                
        def datagramReceived(self, datagram, address):
                print "Received:" + repr(datagram) + " From Address:" + str(address) 
                cmd = string.split(datagram)
                if len(cmd) == 0 or len(cmd) > 3 or cmd[0] != 'easytalk':
                        return
                if cmd[1] == 'join' :
                        findItem = False        
                        for item in self.memberList :       
                                if item.name == cmd[2] and item.address[0] == address[0] :
                                        item.active()
                                        findItem = True
                        if not findItem :
                                self.notifyAll(datagram, address)
                                item = Talker(cmd[2], address)
                                self.memberList.append(item)
                                self.sendMemberList(address)
                                print "Join : ", item.name
                elif cmd[1] == 'leave' :
                        findItem = False        
                        for item in self.memberList :       
                                if item.name == cmd[2] and item.address[0] == address[0] :
                                        self.memberList.remove(item)
                                        self.notifyAll(datagram, address)
                                        findItem = True
                                        print "Leave: ", item.name
                        if not findItem :
                                print "Not Find :" + cmd[2] + " From Address:" + str(address) 
                else :
                        print "Error Received:" + repr(datagram) + " From Address:" + str(address) 


if __name__ == "__main__": 
        mgr = GroupMemberManagerServer()
        mgr.startManager(8008)
        reactor.run()
       