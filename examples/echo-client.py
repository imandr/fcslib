#
# @(#) $Id: echo-client.py,v 1.1 2000/06/04 17:54:15 ivm Exp $
#
# Echo client demo program to illustrate use of SockStream
# class on client side.
# 
# Usage: python ech-client.py <server-host> <server-port> "<message>"
#
# $Log: echo-client.py,v $
# Revision 1.1  2000/06/04 17:54:15  ivm
# Added examples
#
#

from SockStream import SockStream
from socket import *

class	Client:
	def __init__(self, srv_host, srv_port):
		self.Sock = socket(AF_INET, SOCK_STREAM)
		self.Sock.connect(srv_host, srv_port)
		self.Str = SockStream(self.Sock)
		
	def tryIt(self, message):
		return self.Str.sendAndRecv(message)
		
if __name__ == '__main__':
	import sys
	import string
	if len(sys.argv) < 4:
		print 'Usage python echo-client.py <host> <port> <message>'
	else:
		host = sys.argv[1]
		port = string.atoi(sys.argv[2])
		message = sys.argv[3]
		c = Client(host, port)
		answer = c.tryIt(message)
		print 'Message sent:    <%s>' % message
		print 'Answer received: <%s>' % answer
			
			
		
