#
# @(#) $Id: TCPServer.py,v 1.4 2002/05/07 15:25:20 ivm Exp $
#
# $Author: ivm $
#
# $Log: TCPServer.py,v $
# Revision 1.4  2002/05/07 15:25:20  ivm
# Fixed some bugs
# Added Long type to serialize
#
# Revision 1.3  2001/06/12 19:09:23  ivm
# Updated for Python 2.1
#
# Revision 1.2  2000/09/05 18:25:24  ivm
# Do not register TCPServer until it's enabled
#
# Revision 1.1  2000/01/27 20:55:55  ivm
# Initial deposit into FCSLIB
#
# Revision 1.1  2000/01/25 21:27:05  ivm
# Added modules to FBSNG
#
# Revision 1.1  1999/10/01 16:59:02  ivm
# Added TCPServer.py
#
#

from socket import *

class	TCPServer:
	def __init__(self, port, sel, enabled = 1):
		self.Sock = socket(AF_INET, SOCK_STREAM)
		self.Sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.Sock.bind(('', port))
		self.Sel = sel
		if enabled:
			self.enableServer()

	def doRead(self, fd, sel):
		if fd != self.Sock.fileno():
			return
		s, peer = self.Sock.accept()
		if s:
			self.createClientInterface(s, peer, sel)
		
	def createClientInterface(self, sock, peer, sel):
		return None
		pass	# virtual


	def enableServer(self, backlog = 5):
		self.Sock.listen(backlog)
		self.Sel.register(self, rd = self.Sock.fileno())
		
	def disableServer(self):
		self.Sel.unregister(rd = self.Sock.fileno())
		self.Sock.listen(0)
