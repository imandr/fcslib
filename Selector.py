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
        
class   Selector:
        def     __init__(self):
                self.clear()

        def clear(self):
                self.RdObjMap = {}
                self.WrObjMap = {}
                self.ExObjMap = {}
                self.ReadList = []
                self.WriteList = []
                self.ExcList = []
                self.ReadReady = []
                self.WriteReady = []
                self.ExcReady = []

        def     register(self, obj, rd = [], wr = [], ex = []):
                #print 'register: obj=', obj, rd, wr, ex
                if type(rd) != type([]):
                        rd = [rd]
                for fd in rd:
                        if not fd in self.ReadList:
                                self.ReadList.append(fd)
                        self.RdObjMap[fd] = obj
                if type(wr) != type([]):
                        wr = [wr]
                for fd in wr:
                        if not fd in self.WriteList:
                                self.WriteList.append(fd)
                        self.WrObjMap[fd] = obj
                if type(ex) != type([]):
                        ex = [ex]
                for fd in ex:
                        if not fd in self.ExcList:
                                self.ExcList.append(fd)
                        self.ExObjMap[fd] = obj


        def unregisterObject(self, object):
                for fd, obj in self.RdObjMap.items():
                        if obj is object:
                                self.unregister(rd=fd)

                for fd, obj in self.WrObjMap.items():
                        if obj is object:
                                self.unregister(wr=fd)

                for fd, obj in self.ExObjMap.items():
                        if obj is object:
                                self.unregister(ex=fd)

        def unregisterFD(self, fd):
                self.unregister(rd=fd, wr=fd, ex=fd)

        def     unregister(self, rd = [], wr = [], ex = []):
                if type(rd) != type([]):
                        rd = [rd]
                for fd in rd:
                        if fd in self.ReadReady:
                                self.ReadReady.remove(fd)
                        if fd in self.ReadList:
                                self.ReadList.remove(fd)
                        if fd in self.RdObjMap:
                                del self.RdObjMap[fd]
                if type(wr) != type([]):
                        wr = [wr]
                for fd in wr:
                        if fd in self.WriteReady:
                                self.WriteReady.remove(fd)
                        if fd in self.WriteList:
                                self.WriteList.remove(fd)
                        if fd in self.WrObjMap:
                                del self.WrObjMap[fd]
                if type(ex) != type([]):
                        ex = [ex]
                for fd in ex:
                        if fd in self.ExcReady:
                                self.ExcReady.remove(fd)
                        if fd in self.ExcList:
                                self.ExcList.remove(fd)
                        if fd in self.ExObjMap:
                                del self.ExObjMap[fd]

        def     select(self, tmo = 0):
                #print self.RdObjMap
                #print self.WrObjMap
                #print self.ExObjMap
                t0 = time.time()
                timeout = tmo
                again = 1
                while again and (tmo < 0 or time.time() < t0 + tmo):
                        self.ReadReady, self.WriteReady, self.ExcReady = [], [], []
                        try:    self.ReadReady, self.WriteReady, self.ExcReady =  \
                                        select.select(self.ReadList, self.WriteList,
                                                self.ExcList, timeout)
                        except:
                                time.sleep(1)
                        timeout = 0
                        #print 'lists:', self.ReadList, self.WriteList, self.ExcList
                        #print 'ready:', self.ReadReady, self.WriteReady, self.ExcReady

                        again = len(self.ReadReady) + len(self.WriteReady) + \
                                len(self.ExcReady)

                        for fd in self.ReadReady:
                                self.RdObjMap[fd].doRead(fd, self)
                        for fd in self.WriteReady:
                                self.WrObjMap[fd].doWrite(fd, self)
                        for fd in self.ExcReady:
                                self.ExObjMap[fd].doException(fd, self)
                                
                        self.ReadReady = []
                        self.WriteReady = []
                        self.ExcReady = []
                        if not again:
                                break
                return 0

                
                
                                
                                
                                


