#
# @(#) $Id: cvtime.py,v 1.5 2001/06/12 19:07:12 ivm Exp $
#
# cvtime.py is a module of one function which converts text date/time
# specification into absolute time number, returned by time.time()
#
# $Author: ivm $
#
# $Log: cvtime.py,v $
# Revision 1.5  2001/06/12 19:07:12  ivm
# Modified for Python v2.1
#
# Revision 1.4  2000/06/29 22:27:55  ivm
# Added time->string conversion to cvtime
#
# Revision 1.3  2000/06/23 15:40:12  ivm
# Implemented new format of relative time
#
# Revision 1.2  2000/03/14 16:16:06  ivm
# Removed debug print-outs
#
# Revision 1.1  2000/01/27 20:55:56  ivm
# Initial deposit into FCSLIB
#
# Revision 1.1  2000/01/25 21:27:06  ivm
# Added modules to FBSNG
#
# Revision 1.1  1998/10/19 14:04:13  ivm
# Initial deposit
#
#

import string
import time

def _parseTime(str):
	hms = tuple(string.splitfields(str,':'))
	#print hms
	if len(hms) == 1:
		h = hms[0]
		hour = string.atoi(h)
		minute, second = 0, 0
	elif len(hms) == 2:	
		h, m = hms
		hour, minute = string.atoi(h), string.atoi(m)
		second = 0
	else:
		h, m, s = hms
		hour, minute, second = string.atoi(h), string.atoi(m), \
			string.atoi(s)
	return hour, minute, second

def parseDateTime(str):
	s = string.strip(str)
	isl = string.find(s,'/')
	rel = 0
	if s[0] == '+':
		rel = 1
		s = s[1:]
	parts = string.splitfields(s, '-')

	if len(parts) == 1:
		if isl >= 0:
			datestr = parts[0]
			timestr = None
		else:
			timestr = parts[0]
			datestr = None
	else:
		datestr = parts[0]
		timestr = parts[1]

	if rel:
		return _parseRel(datestr, timestr)
	else:
		return _parseAbs(datestr, timestr)

def _parseRel(datestr, timestr):
	t = time.time()
	days, hour, minute, second = None, 0, 0, 0
	
	if datestr == None:	
		# use today's date
		pass
	elif datestr == '':
		# use today's date
		pass
	else:
		days = string.atoi(datestr)
	
	if timestr == None:
		pass
	elif timestr == '':
		pass
	else:
		hour, minute, second = _parseTime(timestr)

	if days == None:
		# days not given, e.g. +01:00:00 = 1 hour from now
		return t + (hour* 60 + minute) * 60 + second
	else:
		# +0-01:00:00 = nearest 1am in future
		# +1-01:00:00 = tomorrow at 1am
		# +2-01:00:00 = 1 am the day after tomorrow
		t = int(t)	# cut fractions
		year_now, month_now, day_now, hour_now, minute_now, second_now, \
			junk, junk, dst = time.localtime(t)
		this_midnight = time.mktime((year_now, month_now, day_now, 
			0, 0, 0, 0, 0, dst))
		tofd_now = (hour_now*60 + minute_now)*60 + second_now
		target_tofd = (hour*60 + minute)*60 + second
		target_t = this_midnight + target_tofd
		daysec = 24*60*60
		target_midnight = this_midnight
		if days == 0 and tofd_now > target_tofd:
				days = 1
		target_t = target_midnight + daysec * days + target_tofd
		return target_t
		
	
	
def _parseAbs(datestr, timestr):
	year, month, day, hour, minute, second, junk, junk, dst = \
		time.localtime(time.time())

	if datestr == None:	
		# use today's date
		pass
	elif datestr == '':
		# use today's date
		pass
	else:
		mdy = tuple(string.splitfields(datestr,'/'))
		if len(mdy) == 1:
			d = mdy[0]
			day = string.atoi(d)
		elif len(mdy) == 2:
			m,d = mdy
			month = string.atoi(m)
			day = string.atoi(d)
		else:
			m,d,y = mdy
			month = string.atoi(m)
			day = string.atoi(d)
			year = string.atoi(y)
	
	if timestr == None:
		# use current time
		pass
	elif timestr == '':
		# midnight
		hour, minute, second = 0,0,0
	else:
		hour, minute, second = _parseTime(timestr)
		#print hour, minute, second
	return time.mktime((year, month, day, hour, minute, second, 0, 0, dst))		 

def dateTime2Str(t):
	year, month, day, hour, minute, second, \
			junk, junk, dst = time.localtime(t)
	return '%02d/%02d/%04d-%02d:%02d:%02d' % (month, day, year, hour, minute,
					second)	
		
if __name__ == '__main__':
	import sys
	while 1:
		print '>',
		t1 = parseDateTime(string.strip(sys.stdin.readline()))
		print time.ctime(t1)
		print dateTime2Str(t1)
		dt = int(t1 - time.time())
		dh = dt/3600
		dt = dt % 3600
		dm = dt/60
		ds = dt % 60
		print '+%d:%d:%d' % (dh, dm, ds)
	

