#
# @(#) $Id: Selector.py,v 1.6 2004/04/05 19:05:25 ivm Exp $
# $Author: ivm $
# $Log: Selector.py,v $
# Revision 1.6  2004/04/05 19:05:25  ivm
# .
#
# Revision 1.5  2003/08/22 18:38:42  ivm
# Implemented floating point values in config
# Fixed typo in Selector.unsubscribeObject
#
# Revision 1.4  2002/05/07 15:25:20  ivm
# Fixed some bugs
# Added Long type to serialize
#
# Revision 1.3  2001/03/26 20:38:48  ivm
# Implemented and improved non-blocking write functionality in SockStream
#
# Revision 1.2  2001/02/28 15:59:48  ivm
# Added non-blocking write support
#
# Revision 1.1  2000/01/27 20:55:55  ivm
# Initial deposit into FCSLIB
#
# Revision 1.1  2000/01/25 21:27:05  ivm
# Added modules to FBSNG
#
# Revision 1.7  1999/09/17 15:00:14  ivm
# Removed returning of errno from Selector.select()
#
# Revision 1.6  1998/09/17 16:00:48  tlevshin
#  instead of list of errno.errorcode now retruns actual errno code, why the
# selection has been interrupted
#
# Revision 1.5  1998/09/14 21:27:18  ivm
# Fix stupid bug. Too ashamed to explain.
#
# Revision 1.4  1998/09/14 19:29:36  ivm
# import time module
#
# Revision 1.3  1998/09/09 21:21:52  ivm
# select() now returns errno in case of problem, 0 otherwise
#
# Revision 1.2  1998/08/18 20:30:11  ivm
# Catch exceptions in select()
#
# Revision 1.1  1998/07/09 15:51:49  ivm
# Initial deposit of Parser.py Selector.py SockStream.py
#
# Revision 1.1  1998/07/03  21:29:00  ivm
# Initial revision
#
# Revision 1.1  1998/07/03  21:28:37  ivm
# Initial revision
#
#
import select
import sys
import time


class	Process:
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
	
class	Selector:
	def	__init__(self):
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

	def	register(self, obj, rd = [], wr = [], ex = []):
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

	def	unregister(self, rd = [], wr = [], ex = []):
		if type(rd) != type([]):
			rd = [rd]
		for fd in rd:
			if fd in self.ReadReady:
				self.ReadReady.remove(fd)
			if fd in self.ReadList:
				self.ReadList.remove(fd)
			if self.RdObjMap.has_key(fd):
				del self.RdObjMap[fd]
		if type(wr) != type([]):
			wr = [wr]
		for fd in wr:
			if fd in self.WriteReady:
				self.WriteReady.remove(fd)
			if fd in self.WriteList:
				self.WriteList.remove(fd)
			if self.WrObjMap.has_key(fd):
				del self.WrObjMap[fd]
		if type(ex) != type([]):
			ex = [ex]
		for fd in ex:
			if fd in self.ExcReady:
				self.ExcReady.remove(fd)
			if fd in self.ExcList:
				self.ExcList.remove(fd)
			if self.ExObjMap.has_key(fd):
				del self.ExObjMap[fd]

	def	select(self, tmo = 0):
		#print self.RdObjMap
		#print self.WrObjMap
		#print self.ExObjMap
		t0 = time.time()
		timeout = tmo
		again = 1
		while again and (tmo < 0 or time.time() < t0 + tmo):
			self.ReadReady, self.WriteReady, self.ExcReady = [], [], []
			try:	self.ReadReady, self.WriteReady, self.ExcReady =  \
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

		
		
				
				
				


