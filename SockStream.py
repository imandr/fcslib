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
#       Creates new SockStream object for given socket. Second parameter
#       is the character to be used as message delimiter
#
# SockStreamLen(sock) -- constructor of SockStreamLen class
#       Creates new SockStreamLen object for given socket.
#
# Rest of methods are the same for both classes
#
# readMore(maxmsg)
#       Read the socket and buffer the information for later decoding
#       and extraction with getMsg method. maxmsg parameter is an integer
#       which specifies maximum number of bytes to read from socket
#       at this time.
#       Returns 1 if there is a complete message in the buffer ready
#       to be extracted with getMsg method.
#       The method will block until data is available for reading from the
#       socket.
#
# getMsg()
#       Unpacks first message available in the buffer and return it
#       as string. If none has been received yet, causes exception.
#       It is recommended to call msgReady method to make sure that getMsg
#       can be called.
#
# msgReady()
#       Returns 1 if there is a complete message in the internal buffer
#       available for unpacking with getMsg method.
#
# send(msg)
#       Sends message appending the end-of-message character at the end
#       of it.
#
# fileno()
#       Returns socket file number. Provided for compatibility with
#       Python select() function. Socket Streams may be grouped in
#       a list and passed to select instead of underlying sockets:
#
#               str1 = SockStream(sock1, myEom)
#               str2 = SockStream(sock2, myEom)
#               read_list, junk, junk = select.select([str1, str2], [], [], 0)
#               if str1 in read_list:
#                       ...
#
# sendAndRecv(msg)
#       Sends the msg, and then waits for first message to arrive. Returns
#       this first message.
#
#
# Advised usage of this class:
# ----------------------------
#
#       sock = socket.socket(...)
#       #...
#       stream = SockStream(sock, myEOM)
#       #...
#       while 1:
#               #...
#               lst, junk, junk = select.select(socklist, [], [], timeout)
#               if sock in lst:
#                       stream.readMore()
#                       while stream.msgReady():
#                               msg = stream.getMsg()
#                               #... process the message
#                       if stream.eof():
#                               # socket is closed -- 
#                               sock.close
#                               # stream object may be deleted
#                               # and the socket should be removed
#                               # from select list
#       
# Keep ALive features
# -------------------
# There are three methods which provide access to this feature:
#
#       zing():         sends Zing message. Remote SockStream object is supposed
#                               to reply with Zong message, not necessarily rigth away.
#                               If by the time the remote SockStream reads from the
#                               socket, there are more than one Zings buffered,
#                               only one Zong is sent back.
#       probe():        sends Probe message. Unlike Zing, Probe does not
#                               require any response from the remote SockStream
#       lastHeard():
#                               returns how long ago (in seconds) anything was heard from the 
#                               remote SockStream. "Anything" includes regular communication,
#                               probes, zings and zongs.
#
#       SockStream constructor has 3 additional optional parameters which
#       can be used to specify custom Probe, Zing and Zong messages
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
#       - network outage with remote host and SockStream OK
#       - remote host is down
#       - the peer is too busy to answer in time
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

def to_bytes(s):
    if isinstance(s, str):
        s = bytes(s, "utf-8")
    return s
    
def to_str(b):
    if isinstance(b, bytes):
        b = b.decode("utf-8")
    return b

class   SockStream:
        def     __init__(self, sock,  
                        eom = b'\n', probe = b'\t', zing = b'', zong = b' ', sel = None):
                self.Buf = b''
                self.Sock = sock
                self.Eom = eom
                self.Zing = zing
                self.Zong = zong
                self.Probe = probe
                self.EOF = 0
                self.LastTxn = time.time()
                self.OutBuf = b''
                self.Sel = sel
                                
        def _zingZong(self):
                buf = self.Buf
                newBuf = b''
                inx = buf.find(self.Eom)
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
                        buf = buf[inx+len(self.Eom):]           # skip EOM
                        inx = buf.find(self.Eom)                
                self.Buf = newBuf + buf
                
        def setBlocking(self, block):
                self.Sock.setblocking(block)
                
        def readMore(self, maxmsg = 1024, tmo = -1):
                if not self.EOF:
                        msg = b''
                        if tmo == -1:   tmo = None
                        fd = self.Sock.fileno()
                        r,w,e = select.select([fd],[],[],tmo)
                        if not r:
                                raise IOError('Time-out')
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

        def getMsg(self):
                if self.Eom in self.Buf:
                    msg, self.Buf = self.Buf.split(self.Eom, 1)
                    return to_str(msg)
                else:
                    return None

        def msgReady(self):
            #print("msgReady: buf: %s, eom: %s" % (repr(self.Buf), repr(self.Eom)))
            return self.Eom in self.Buf

        def send(self, msg, tmo = -1):
                # send one or list of messages
                if not isinstance(msg, list):
                        msg = [msg]
                nsent = 0
                while msg:
                        n = min(100, len(msg))
                        batch = msg[:n]
                        msg = msg[n:]
                        batch = (to_bytes(x) for x in batch)
                        text = self.Eom.join(batch) + self.Eom
                        ns = self._send(text, tmo)
                        if ns <= 0:     break
                        nsent = nsent + ns
                return nsent                    

        def     _send(self, data, tmo = -1):
                #print 'SockStream.send(msg = <%s>)' % msg
                self.OutBuf = self.OutBuf + data
                nsent = 0
                if tmo == -1:   tmo = None
                while self.OutBuf and not self.EOF:
                        #print 'SockStream.send(): msg = <%s>, nsent = %d' % (msg, nsent)
                        # use select to wait for socket buffer to clear at least 1 byte
                        r,w,e = select.select([],[self.Sock.fileno()],[],tmo)
                        if not w:
                                break
                        n = -1
                        try:    n = self.Sock.send(self.OutBuf)
                        except socket.error as val:
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
                                self.OutBuf = b''
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

        def fileno(self):
                return self.Sock.fileno()

        def eof(self):
                return not self.msgReady() and self.EOF

        def recv(self, maxmsg=1024, tmo = -1):
                if not self.msgReady():
                        while not self.readMore(maxmsg, tmo):
                                if self.eof():
                                        return None
                return self.getMsg()

        def sendAndRecv(self, msg, tmo = -1):
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
                
class   SockStreamLen:
        # these strings MUST be 6 characters long
        #       '123456'
        Zing =  '.zing.'
        Zong =  '.zong.'
        Probe = '.probe'

        def     __init__(self, sock):
                self.Buf = b''
                self.MsgLen = None
                self.Sock = sock
                self.EOF = 0
                self.LastTxn = time.time()

        def     readMore(self, maxmsg = 1024):
                if not self.EOF:
                        msg = b''
                        try:    msg = self.Sock.recv(maxmsg)
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
                        try:    l = int(lbuf)
                        except:
                                if lbuf == self.Zing and not zongSent:
                                        self._sendZong()
                                        zongSent = 1
                        else:
                                self.MsgLen = l
                                return
                
        def lastHeard(self):
                return time.time() - self.LastTxn

        def     getMsg(self):
                msg = self.Buf[:self.MsgLen]
                self.Buf = self.Buf[self.MsgLen:]
                self.getMsgLen()
                return msg

        def     msgReady(self):
                return self.MsgLen != None and len(self.Buf) >= self.MsgLen

        def     send(self, msg):
                try:    n = self.Sock.send(b'%06d%s' % (len(msg), msg))
                except:
                        return 0
                else:
                        return n

        def     fileno(self):
                return self.Sock.fileno()

        def     eof(self):
                return not self.msgReady() and self.EOF

        def recv(self, maxmsg=1024):
                if not self.msgReady():
                        while not self.readMore(maxmsg):
                                if self.eof():
                                        return None
                return self.getMsg()

        def     sendAndRecv(self, msg):
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
