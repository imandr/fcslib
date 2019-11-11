from .SockStream import *
import sys, select, time
from pythreader import Task

class   TCPClientConnectionTask(Task):
        def __init__(self, sock, addr):
            Task.__init__(self)
            self.Str = SockStream(sock)
            self.Sock = sock
            self.Disconnected = False
            self.LastIdle = 0.0
                
        def run(self):
            while not self.Disconnected:
                fd = self.Sock.fileno()
                #print("TCPClientConnectionTask: select...")
                r,w,e = select.select([fd],[],[fd], 1.0)
                #print("TCPClientConnectionTask: r,w,e:", r, w, e)
                if fd in r or fd in e:
                    self.doRead(fd)
                else:
                    t = time.time()
                    self.idle(t, self.LastIdle)
                    self.LastIdle = t
                
                        
        def doRead(self, fd):
                if fd != self.Str.fileno():
                        return
                self.Str.readMore()
                while not self.Disconnected and self.Str.msgReady():
                        msg = self.Str.getMsg()
                        if not msg: continue
                        words = msg.split()
                        if not words:   continue
                        #print words
                        ans = self.processMsg(words[0], words[1:], msg)
                        #print 'ans=<%s>' % ans
                        if ans != None and self.Str !=  None:
                                self.Str.send(ans)
                if not self.Disconnected and self.Str.eof():
                        self.disconnect()
                        
        def disconnect(self, msg = None):
                if not self.Disconnected:
                        if msg:
                                self.send(msg)
                        self.Disconnected = True
                        self.Sock.close()
                        self.Str = None
                        self.eof()

        def send(self, msg):
                if not self.Disconnected:
                        self.Str.send(msg)

        def sendAndRecv(self, msg):
                if not self.Disconnected:
                        return self.Str.sendAndRecv(msg)
                else:
                        return None

        # overridables
        def idle(self, now, last_idle):
            pass
            
        def processMsg(self, cmd, args, msg):
                return None
                
        def eof(self):
                pass
