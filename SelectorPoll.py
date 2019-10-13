
import select
import sys
import time


class   Process:
        #
        # Abstract class. Must have following functions. Selector
        # will call those:
        #
        # doRead(self, fd, selector)
        #
        # doWrite(self, fd, selector)
        #
        # doException(self, fd, selector)
        #
        def __init__(self):
                pass
        
class   SelectorPoll:

    def     __init__(self):
            self.clear()

    def clear(self):
            self.Poll = select.poll()
            self.RdObjMap = {}          # {int fd -> (object, file_or_fd)
            self.WrObjMap = {}
            self.ExObjMap = {}

    def     register(self, obj, rd = [], wr = [], ex = []):

            if type(rd) != type([]):
                    rd = [rd]
            if type(wr) != type([]):
                    wr = [wr]
            if type(ex) != type([]):
                    ex = [ex]

            for fd in rd:   self.registerRead(fd, obj)
            for fd in wr:   self.registerWrite(fd, obj)
            for fd in ex:   self.registerError(fd, obj)
        
    def registerRead(self, fd, obj):
        return self._register(fd, obj, self.RdObjMap)

    def registerWrite(self, fd, obj):
        return self._register(fd, obj, self.WrObjMap)

    def registerError(self, fd, obj):
        return self._register(fd, obj, self.ExObjMap)

    def _register(self, f_or_fd, obj, mapdict):
        fd = f_or_fd
        if type(fd) != type(1): fd = f_or_fd.fileno()
        mapdict[fd] = (obj, f_or_fd)
        self._updatePoll(fd)
        
    def _updatePoll(self, fd):
        mask = 0
        if self.RdObjMap.has_key(fd):   mask |= select.POLLIN
        if self.WrObjMap.has_key(fd):   mask |= select.POLLOUT
        if self.ExObjMap.has_key(fd):   mask |= select.POLLERR | select.POLLHUP
        if mask:    self.Poll.register(fd, mask)
        else:
            try:    self.Poll.unregister(fd)
            except KeyError:    pass

    def unregisterObject(self, object):

            for fd, (obj, f_or_fd) in self.RdObjMap.items():
                    if obj is object:
                            self.unregisterRead(fd)

            for fd, (obj, f_or_fd) in self.WrObjMap.items():
                    if obj is object:
                            self.unregisterWrite(fd)

            for fd, (obj, f_or_fd) in self.ExObjMap.items():
                    if obj is object:
                            self.unregisterError(fd)

    def unregisterRead(self, fd):
        return self._unregister(fd, self.RdObjMap)

    def unregisterWrite(self, fd):
        return self._unregister(fd, self.WrObjMap)

    def unregisterError(self, fd):
        return self._unregister(fd, self.ExObjMap)
        
    def _unregister(self, fd, mapdict):
        if mapdict.has_key(fd): del mapdict[fd]
        self._updatePoll(fd)

    def unregisterFD(self, fd):
            self.unregisterRead(fd)
            self.unregisterWrite(fd)
            self.unregisterError(fd)

    def select(self, tmo = 0):
            #print self.RdObjMap
            #print self.WrObjMap
            #print self.ExObjMap
            t0 = time.time()
            timeout = tmo
            again = True
            while again and (tmo < 0 or time.time() < t0 + tmo):
                results = []
                try:    results = self.Poll.poll(timeout)
                except:
                        time.sleep(1)
                again = not not results
                for fd, mask in results:
                    if mask & select.POLLIN:
                        obj, f_or_fd = self.RdObjMap.get(fd, (None, None))
                        if obj != None:
                            obj.doRead(f_or_fd, self)

                    if mask & select.POLLOUT:
                        obj, f_or_fd = self.WrObjMap.get(fd, (None, None))
                        if obj != None:
                            obj.doWrite(f_or_fd, self)

                    if mask & (select.POLLERR | select.POLLHUP):
                        obj, f_or_fd = self.ExObjMap.get(fd, (None, None))
                        if obj != None:
                            obj.doException(f_or_fd, self)

            return 0








