from socket import *
import time, select
from pythreader import PyThread, TaskQueue, synchronized

class   TCPServerThread(PyThread):
        def __init__(self, port, ip='', max_clients = None, queue_capacity = None, stagger=None, enabled = True):
                PyThread.__init__(self)
                self.Sock = None
                self.Clients = TaskQueue(max_clients, capacity=queue_capacity, stagger=stagger)
                self.Port = port
                self.IP = ip
                self.Enabled = enabled
                self.Shutdown = False
                self.LastIdle = 0.0
                        
        def run(self):
            self.Sock = socket(AF_INET, SOCK_STREAM)
            self.Sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.Sock.bind((self.IP, self.Port))
            if self.Enabled:    
                self.enable()
            while not self.Shutdown:
                fd = self.Sock.fileno()
                #print("TCPServerThread: select...")
                r,w,e = select.select([fd],[fd],[fd], 1.0)
                #print("TCPServerThread: r,w,e:", r, w, e)
                if fd in r or fd in e or fd in w:
                    csock, caddr = self.Sock.accept()
                    task = self.createClientInterface(csock, caddr)
                    #print ("TCPServerThread: client task created:", task)
                    if task is not None:
                        self.Clients.addTask(task)
                else:
                    t = time.time()
                    self.idle(t, self.LastIdle)
                    self.LastIdle = t
            self.Sock.close()

        @synchronized
        def enable(self, backlog = 5):
                if self.Sock is not None:
                    self.Sock.listen(backlog)
                self.Clients.release()
                self.Enabled = True
                
        @synchronized
        def disable(self):
                self.Sock.listen(0)
                self.Clients.hold()
                self.Enabled = False
                
        def shutdown(self):
            self.Shutdown = True
                
        def waitForClients(self):
            self.Clients.waitUntilEmpty()
            
        # overridables                
        def idle(self, now, last_idle):
            pass
        
        def createClientInterface(self, sock, addr):
                return None
                pass    # virtual

