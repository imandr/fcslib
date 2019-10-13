#
# @(#) $Id: SockStream.py,v 1.11 2003/02/25 15:35:32 ivm Exp $
#
# $Author: ivm $
#
# $Log: SockStream.py,v $
# Revision 1.11  2003/02/25 15:35:32  ivm
# *** empty log message ***
#
# Revision 1.10  2002/08/16 17:58:07  ivm
# Make suze serialized long ends with L even in Python 2.x
#
# Revision 1.9  2001/05/25 20:18:56  ivm
# Catch would-block exception in non-blocking send
#
# Revision 1.8  2001/03/27 22:31:02  ivm
# Moved sel parameter of constructor to the end
#
# Revision 1.7  2001/03/26 20:38:48  ivm
# Implemented and improved non-blocking write functionality in SockStream
#
# Revision 1.6  2001/02/28 15:59:48  ivm
# Added non-blocking write support
#
# Revision 1.5  2000/03/30 17:21:06  ivm
# Allow lists in send()
#
# Revision 1.4  2000/03/07 17:27:33  ivm
# Fixed bug with multiple EOMs in send()
#
# Revision 1.3  2000/03/02 22:33:29  ivm
# Added time-outs to recv, send and sendAndRecv of SockStream
#
# Revision 1.1  2000/01/27 20:55:55  ivm
# Initial deposit into FCSLIB
#
# Revision 1.1  2000/01/25 21:27:05  ivm
# Added modules to FBSNG
#
# Revision 1.14  1999/10/11 19:54:03  ivm
# Fixed MsgLen in SockStreamLen
#
# Revision 1.13  1999/09/21 15:55:37  ivm
# Added SockStreamLen class
#
# Revision 1.12  1999/06/01 19:28:39  ivm
# Fixed pinging, added recv() method
#
# Revision 1.6  1999/06/01  19:27:44  ivm
# Pinging implemented
#
# Revision 1.5  1999/06/01  18:25:15  ivm
# Got SockStream from FBS library to get keep-alive functons
#
# Revision 1.11  1999/03/09 17:52:09  ivm
# Fixed zing(): just set EOF, do not close the socket
#
# Revision 1.10  1999/03/09 17:41:48  ivm
# Added optional timeout parameter to zing()
#
# Revision 1.9  1999/02/26 16:35:39  ivm
# maxmsg parameter in readMore is defaulted to 1024
#
# Revision 1.7  1999/02/26 16:17:39  ivm
# Fixed couple bugs in SockStream. Added echo-cln and echo-srv demos.
#
# Revision 1.5  1998/08/07 20:05:28  ivm
# Tested with JobStat client
#
# Revision 1.4  1998/07/23 16:58:13  ivm
# Be careful not to call recv() in readMore() if EOF flag is set.
# Catch and ignore any exceptions when calling recv().
#
# Revision 1.3  1998/07/17 14:28:55  ivm
# send() method now catches exceptions and returns 0 in case of error
#
# Revision 1.3  1998/07/17 14:26:58  ivm
# send() will catch exceptions and return 0 in case of error.
#
# Revision 1.2  1998/07/13 16:17:05  ivm
# Get rid of exception on EOF, use eof() method instead
#
# Revision 1.1  1998/07/09 15:10:29  ivm
# Initial revision
#
# Revision 1.1  1998/07/03  21:29:00  ivm
# Initial revision
#
# Revision 1.1  1998/07/03  21:28:37  ivm
# Initial revision
#
#
#
# SockStream and SockStreamLen classes are used to send/receive messages 
# over TCP socket stream. Messages in the stream are separated with user 
# defined end-of-message character for SockStream class, and are prepended
# with 6-digit message length for SockStreamLen class. SockStreamLen
# class should be used when it's impossible to predict what character
# may not be included in user a message (e.g. when sending binary data).
#
# Public methods of both classes are:
#
# SockStream(sock, eom) -- constructor of SockStream class
#	Creates new SockStream object for given socket. Second parameter
#	is the character to be used as message delimiter
#
# SockStreamLen(sock) -- constructor of SockStreamLen class
#	Creates new SockStreamLen object for given socket.
#
# Rest of methods are the same for both classes
#
# readMore(maxmsg)
#	Read the socket and buffer the information for later decoding
#	and extraction with getMsg method. maxmsg parameter is an integer
#	which specifies maximum number of bytes to read from socket
#	at this time.
#	Returns 1 if there is a complete message in the buffer ready
#	to be extracted with getMsg method.
#	The method will block until data is available for reading from the
#	socket.
#
# getMsg()
#	Unpacks first message available in the buffer and return it
#	as string. If none has been received yet, causes exception.
#	It is recommended to call msgReady method to make sure that getMsg
#	can be called.
#
# msgReady()
#	Returns 1 if there is a complete message in the internal buffer
#	available for unpacking with getMsg method.
#
# send(msg)
#	Sends message appending the end-of-message character at the end
#	of it.
#
# fileno()
#	Returns socket file number. Provided for compatibility with
#	Python select() function. Socket Streams may be grouped in
#	a list and passed to select instead of underlying sockets:
#
#		str1 = SockStream(sock1, myEom)
#		str2 = SockStream(sock2, myEom)
#		read_list, junk, junk = select.select([str1, str2], [], [], 0)
#		if str1 in read_list:
#			...
#
# sendAndRecv(msg)
#	Sends the msg, and then waits for first message to arrive. Returns
#	this first message.
#
#
# Advised usage of this class:
# ----------------------------
#
#	sock = socket.socket(...)
#	#...
#	stream = SockStream(sock, myEOM)
#	#...
#	while 1:
#		#...
#		lst, junk, junk = select.select(socklist, [], [], timeout)
#		if sock in lst:
#			stream.readMore()
#			while stream.msgReady():
#				msg = stream.getMsg()
#				#... process the message
#			if stream.eof():
#				# socket is closed -- 
#				sock.close
#				# stream object may be deleted
#				# and the socket should be removed
#				# from select list
#	
# Keep ALive features
# -------------------
# There are three methods which provide access to this feature:
#
#	zing(): 	sends Zing message. Remote SockStream object is supposed
#				to reply with Zong message, not necessarily rigth away.
#				If by the time the remote SockStream reads from the
#				socket, there are more than one Zings buffered,
#				only one Zong is sent back.
#	probe():	sends Probe message. Unlike Zing, Probe does not
#				require any response from the remote SockStream
#	lastHeard():
#				returns how long ago (in seconds) anything was heard from the 
#				remote SockStream. "Anything" includes regular communication,
#				probes, zings and zongs.
#
#	SockStream constructor has 3 additional optional parameters which
#	can be used to specify custom Probe, Zing and Zong messages
#
# Effect of Keep Alive on normal communication
# --------------------------------------------
# Zing, Zong and Probe are messages which SockStream's client never sees.
# The suggested usage of SockStream outlined above DOES NOT change.
# The only effect which this feature may have on clients is that
# it will be more frequent event that after "readMore" no message
# is ready (readMore() and msgReady() return FALSE).
# If one peer uses this feature, it does not mean that the other has
# to use it.
#
# By default, Zing is empty message, Zong is space (' '), and Probe is 
# tab ('\t'). If those messages are to be used for regular communication,
# those defaults should be overriden.
#
# Suggested use of Keep Alive feature
# -----------------------------------
# 1. Just probing: client periodically calls probe() method without
# checking lastHeard(). This will allow detection of the event when
# remote host goes down and then recovers. When it recovers, after several
# probes, the socket will be closed and next time SockStream.eof() will return
# TRUE.
#
# 2. Zinging: client periodically calls zing() and lastHeard() methods.
# Zings are supposed to cause some response from the remote SockStream.
# If lastHeard() indicates that the remote SockStream does not answer
# for reasonably long time, after reasonably many Zings sent, it can
# be interpreted as one or combination of the following:
#	- network outage with remote host and SockStream OK
#	- remote host is down
#	- the peer is too busy to answer in time
# There is a shortcut. If client provides optinal time-out measured in
# seconds as an argument to zing(), SockClient itself checks for time-out
# and closes the socket, so that next readMore() will generate EOF condition
# for the SockStream.
#
# 3. Combination of zinging and probing, of course can be used too
#
import string
import time
import select
import sys
import os
import errno
import socket

class	SockStream:
	def	__init__(self, sock,  
			eom = '\n', probe = '\t', zing = '', zong = ' ', sel = None):
		self.Buf = ''
		self.Sock = sock
		self.Eom = eom
		self.Zing = zing
		self.Zong = zong
		self.Probe = probe
		self.EOF = 0
		self.LastTxn = time.time()
		self.OutBuf = ''
		self.Sel = sel
				
	def _zingZong(self):
		buf = self.Buf
		newBuf = ''
		inx = string.find(buf, self.Eom)
		zongSent = 0		
		while inx >= 0:
			msg = buf[:inx]
			if msg == self.Zing:
				#print 'Got Zing'
				if not zongSent:
					self.send(self.Zong)
					zongSent = 1
			elif msg != self.Probe and msg != self.Zong:
				newBuf = newBuf + msg + self.Eom
			buf = buf[inx+len(self.Eom):]		# skip EOM
			inx = string.find(buf, self.Eom)		
		self.Buf = newBuf + buf
		
	def setBlocking(self, block):
		self.Sock.setblocking(block)
		
	def	readMore(self, maxmsg = 1024, tmo = -1):
		if not self.EOF:
			msg = ''
			if tmo == -1:	tmo = None
			fd = self.Sock.fileno()
			r,w,e = select.select([fd],[],[],tmo)
			if not r:
				raise IOError, 'Time-out'
			try:	
				msg = self.Sock.recv(maxmsg)
				#print 'SockStream.readMore: msg=<%s>' % msg
			except: 
				#print 'readMore: exception: ', sys.exc_type, sys.exc_value
				#print 'readMore: EOF -> 1'
				self.EOF = 1
			if len(msg) == 0:
				#print 'readMore: len = 0'
				#print 'readMore: EOF -> 1'
				self.EOF = 1
				self.unregister()
			else:
				self.LastTxn = time.time()
				self.Buf = self.Buf + msg
				self._zingZong()
		return self.msgReady()

	def lastHeard(self):
		return time.time() - self.LastTxn

	def	getMsg(self):
		i = string.find(self.Buf, self.Eom)
		if i < 0:
			return None
		str =  self.Buf[:i]
		self.Buf = self.Buf[i+len(self.Eom):]		# skip EOM
		return str

	def	msgReady(self):
		inx = string.find(self.Buf, self.Eom)
		ok = inx >= 0
		return ok

	def send(self, msg, tmo = -1):
		# send one or list of messages
		if type(msg) != type([]):
			msg = [msg]
		nsent = 0
		while msg:
			n = min(100, len(msg))
			str = string.join(msg[:n], self.Eom) + self.Eom
			ns = self._send(str, tmo)
			if ns <= 0: 	break
			msg = msg[n:]
			nsent = nsent + ns
		return nsent			

	def	_send(self, data, tmo = -1):
		#print 'SockStream.send(msg = <%s>)' % msg
		self.OutBuf = self.OutBuf + data
		nsent = 0
		if tmo == -1:	tmo = None
		while self.OutBuf and not self.EOF:
			#print 'SockStream.send(): msg = <%s>, nsent = %d' % (msg, nsent)
			# use select to wait for socket buffer to clear at least 1 byte
			r,w,e = select.select([],[self.Sock.fileno()],[],tmo)
			if not w:
				break
			n = -1
			try:	n = self.Sock.send(self.OutBuf)
			except socket.error, val:
				errn, msg = val.args
				if errn == errno.EWOULDBLOCK:
					n = 0
				else:
					n = -1
			except:
				# n will be -1 here
				# print sys.exc_type, sys.exc_value
				pass
			#print 'n = ', n
			if n == -1:
				self.EOF = 1
				self.OutBuf = ''
			elif n > 0:
				nsent = nsent + n
				self.OutBuf = self.OutBuf[n:]

		if self.Sel:
			if self.OutBuf and not self.EOF:
				self.Sel.register(self, wr = self.Sock.fileno())
			else:
				self.unregister()

		return nsent

	def resend(self, tmo = 0):
		return self._send('',tmo)

	def	fileno(self):
		return self.Sock.fileno()

	def	eof(self):
		return not self.msgReady() and self.EOF

	def recv(self, maxmsg=1024, tmo = -1):
		if not self.msgReady():
			while not self.readMore(maxmsg, tmo):
				if self.eof():
					return None
		return self.getMsg()

	def	sendAndRecv(self, msg, tmo = -1):
		self.send(msg, tmo = tmo)
		return self.recv(tmo = tmo)

	def zing(self, tmo = None):
		if tmo != None and self.lastHeard() > tmo:
			self.EOF = 1
		else:	
			self.send(self.Zing)
	
	def probe(self):
		self.send(self.Probe)

	def doWrite(self, fd, sel):
		if fd != self.Sock.fileno():
			return
		self.resend()
		if not self.OutBuf or self.EOF:
			self.unregister()

	def unregister(self):
		if self.Sel:
			self.Sel.unregisterObject(self)

	def outBufLen(self):
		return len(self.OutBuf)

	def close(self):
		if self.Sel:
			self.unregister()
		self.Sock.close()
		
class	SockStreamLen:
	# these strings MUST be 6 characters long
	#   	'123456'
	Zing =  '.zing.'
	Zong =  '.zong.'
	Probe = '.probe'

	def	__init__(self, sock):
		self.Buf = ''
		self.MsgLen = None
		self.Sock = sock
		self.EOF = 0
		self.LastTxn = time.time()

	def	readMore(self, maxmsg = 1024):
		if not self.EOF:
			msg = ''
			try:	msg = self.Sock.recv(maxmsg)
			except: 
				self.EOF = 1
			if len(msg) == 0:
				self.EOF = 1
			else:
				self.LastTxn = time.time()
				self.Buf = self.Buf + msg
				if self.MsgLen == None:
					self.getMsgLen()
					# take care of zings here, later
		return self.msgReady()

	def getMsgLen(self):
		# does zing-zong too
		zongSent = 0
		self.MsgLen = None
		while len(self.Buf) >= 6:
			lbuf = self.Buf[:6]
			self.Buf = self.Buf[6:]
			try:	l = string.atoi(lbuf)
			except:
				if lbuf == self.Zing and not zongSent:
					self._sendZong()
					zongSent = 1
			else:
				self.MsgLen = l
				return
		
	def lastHeard(self):
		return time.time() - self.LastTxn

	def	getMsg(self):
		msg = self.Buf[:self.MsgLen]
		self.Buf = self.Buf[self.MsgLen:]
		self.getMsgLen()
		return msg

	def	msgReady(self):
		return self.MsgLen != None and len(self.Buf) >= self.MsgLen

	def	send(self, msg):
		try:	n = self.Sock.send('%06d%s' % (len(msg), msg))
		except:
			return 0
		else:
			return n

	def	fileno(self):
		return self.Sock.fileno()

	def	eof(self):
		return not self.msgReady() and self.EOF

	def recv(self, maxmsg=1024):
		if not self.msgReady():
			while not self.readMore(maxmsg):
				if self.eof():
					return None
		return self.getMsg()

	def	sendAndRecv(self, msg):
		self.send(msg)
		return self.recv()

	def zing(self, tmo = None):
		if tmo != None and self.lastHeard() > tmo:
			self.EOF = 1
		else:	
			self.Sock.send(self.Zing)
	
	def probe(self):
		self.Sock.send(self.Probe)

	def _sendZong(self):
		self.Sock.send(self.Zong)