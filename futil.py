#
# @(#) $Id: futil.py,v 1.4 2002/05/07 15:25:20 ivm Exp $
#
# $Author: ivm $
#
#	Collection of general-purpose file system utilities.
#	Currently, there is one function here:
#
#	rmdirrec(path)	- equivalent of "rm -rf", deletes the specified
#					directory and all files/directories underneath it.
#
# $Log: futil.py,v $
# Revision 1.4  2002/05/07 15:25:20  ivm
# Fixed some bugs
# Added Long type to serialize
#
# Revision 1.3  2000/07/25 17:29:36  ivm
# Do not use os.path module. It is unavailable in Python 1.5.1
#
# Revision 1.2  2000/06/30 13:55:28  ivm
# Use os.path module
#
# Revision 1.1  2000/01/27 20:55:56  ivm
# Initial deposit into FCSLIB
#
# Revision 1.1  2000/01/25 21:27:06  ivm
# Added modules to FBSNG
#
# Revision 1.3  1999/10/20 21:18:35  ivm
# Fixed futil for Linux
# Fixed ConfigFile::getValueList() returning None
#
# Revision 1.2  1999/09/15 19:29:05  ivm
# Added keep_root argument to rmdirrec()
#
# Revision 1.1  1999/08/16 20:30:48  ivm
# Added futil.py
#
#

import os
import errno
import stat

def is_dir(path):
	try:	return stat.S_ISDIR(os.stat(path)[stat.ST_MODE])
	except: return 0

def is_link(path):
	try:	return stat.S_ISLNK(os.lstat(path)[stat.ST_MODE])
	except: return 0

def rmdirrec(path, keep_root = 0):
	lst = os.listdir(path)
	for n in lst:
		p = path + '/' + n
		# try to remove it
		if is_link(p):
			os.unlink(p)
		elif is_dir(p):
			rmdirrec(p)
		else:
			os.unlink(p)
	if not keep_root:
		os.rmdir(path)

if __name__ == '__main__':
	import sys
	rmdirrec(sys.argv[1])
