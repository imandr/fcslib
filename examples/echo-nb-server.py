#
# @(#) $Id: echo-nb-server.py,v 1.1 2001/02/28 16:57:37 ivm Exp $
#
# Echo server demo program to illustrate use of SockStream, TCPServer
# and Selector on server side. Serves multiple clients.
# 
# Usage: python ech-server.py <port>
#
# $Log: echo-nb-server.py,v $
# Revision 1.1  2001/02/28 16:57:37  ivm
# Added nb server example
#
# Revision 1.1  2000/06/04 17:54:15  ivm
# Added examples
#
#

from TCPServer import *
from SockStream import SockStream

class	EchoSrv(TCPServer):
	def __init__(self, port, sel):
		TCPServer.__init__(self, port, sel)
		print 'Server socket #%d' % self.Sock.fileno()
			
	def createClientInterface(self, sock, addr, sel):
		print 'New client at ', addr, ' socket #%d' % sock.fileno()
		return EchoClient(sock, addr, sel)
		
class	EchoClient:
	def __init__(self, sock, addr, sel):
		self.Sock = sock
		self.Str = SockStream(sock, sel=sel)
		self.Str.setBlocking(0)
		self.Addr = addr
		self.Sel = sel
		sel.register(self, rd=sock.fileno())
		
	def doRead(self, fd, sel):
		if fd == self.Sock.fileno():
			self.Str.readMore()
			while self.Str.msgReady():
				msg = self.Str.getMsg()
				self.Str.send(msg,0)
			if self.Str.eof():
				# client disconnected
				print 'Client ',self.Addr, 'disconnected'
				sel.unregister(rd=self.Sock.fileno())
				self.Str = None
				self.Sock.close()
				
if __name__=='__main__':
	from Selector import *
	import string
	import sys
	if len(sys.argv) < 2:
		print 'Usage: python ech-server.py <port>'
	else:
		sel=Selector()
		srv = EchoSrv(string.atoi(sys.argv[1]), sel)
		while 1:
			sel.select(10)

