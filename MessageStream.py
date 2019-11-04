import time
from socket import timeout as socket_timeout

class Timeout(Exception):
    pass
    
class ProtocolError(Exception):
    def __init__(self, header):
        self.Header = header
        
    def __str__(self):
        return "ProtocolError: header: %s" % (self.Header,)

def to_bytes(s):
    if isinstance(s, str):
        s = bytes(s, "utf-8")
    return s
    
def to_str(b):
    if isinstance(b, bytes):
        b = b.decode("utf-8")
    return b

class MessageStream(object):
    
    VERSION = "1.0"
    
    def __init__(self, sock):
        self.Sock = sock
        self.EOF = False
        
    def send(self, msg, tmo=None):
        header = "M:%10s:%020d:" % (self.VERSION, len(msg))
        saved_tmo = self.Sock.gettimeout()
        self.Sock.settimeout(tmo)
        try:        
            self.Sock.sendall(to_bytes(header)+to_bytes(msg))
            print ("send: sent successfully")
            return True
        except socket_timeout:
            raise Timeout()
        finally:
            self.Sock.settimeout(saved_tmo)
        
    def zing(self):
        self.Sock.sendall(b"Z:")
        
    def _read_n(self, n, t1=None):
        if n <= 0:  return b''
        t0 = time.time()
        nread = 0
        n_to_read = n
        data_read = b''
        saved_tmo = self.Sock.gettimeout()
        try:
            while (t1 is None or time.time() < t1) and n_to_read > 0:
                d = None if t1 is None else max(0.0, t1-time.time())
                self.Sock.settimeout(d)
                data = self.Sock.recv(n_to_read)
                if not len(data):
                    return data_read
                data_read += data
                n_to_read -= len(data)
        except socket_timeout:
            raise Timeout()
        except:
            self.EOF = True
        finally:
            self.Sock.settimeout(saved_tmo)
        return data_read
            
    def _recv_msg(self, t1=None):
        h = self._read_n(2, t1)
        if len(h) != 2:   return None, None     # EOF
        if h == b'Z:':
            return 'Z', None
        if h == b'z:':
            return 'z', None
        elif h == b'M:':
            #header = "M:%10s:%020d:" % (self.VERSION, len(msg))
            hdr = self._read_n(32, t1)
            if len(hdr) != 32:  return None, None       # EOF
            hdr = to_str(hdr)
            if hdr[10] != ':' or hdr[-1] != ':':
                raise ProtocolError(hdr)
            version = to_str(hdr[:10]).strip()
            try:
                size = int(hdr[11:-1])
            except:
                raise ProtocolError(hdr[11:-1])
            data = self._read_n(size) if size > 0 else b''
            return 'M', data
        else:
            raise ProtocolError(h)
            
    def recv(self, tmo=None):
        t1 = None if tmo is None else time.time() + tmo
        while self.Sock is not None and not self.EOF:
            t, data = self._recv_msg(t1)
            if t == 'Z':
                self.Sock.sendall(b'z:')            # send zong
            elif t == 'z':
                pass                                # ignore zongs
            elif t == 'M':
                return data
            elif t is None:
                self.EOF = True
                return None
            else:
                raise ProtocolError(t)
        return None
        
    def sendAndRecv(self, msg, tmo=None):
        self.send(msg, tmo)
        return self.recv(tmo)
        
    def close(self):
        self.EOF = True
        self.Sock.close()
        self.Sock = None
        
if __name__ == '__main__':
    import sys
    from socket import *
    
    if sys.argv[1] == 'server':
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(('', 3456))
        sock.listen()
        s, addr = sock.accept()
        stream = MessageStream(s)
        while True:
            stream.zing()
            msg = stream.recv()
            print ("server: received:", msg)
            if msg is None:
                print("EOF")
                break
            stream.send(b"echo: "+msg)
    
    else:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(('127.0.0.1', 3456))
        stream = MessageStream(sock)
        while True:
            reply = stream.sendAndRecv("hello %f" % (time.time(),))
            print("client: reply:", reply)
            time.sleep(3)
        
            
            