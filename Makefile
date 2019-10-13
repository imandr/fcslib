#
# @(#) $Id: Makefile,v 1.17 2003/08/25 17:02:11 ivm Exp $
#
# $Log: Makefile,v $
# Revision 1.17  2003/08/25 17:02:11  ivm
# v2_1a
#
# Revision 1.16  2002/05/07 15:25:20  ivm
# Fixed some bugs
# Added Long type to serialize
#
# Revision 1.15  2001/06/12 19:07:12  ivm
# Modified for Python v2.1
#
# Revision 1.14  2001/03/26 20:39:45  ivm
# v2_0
#
# Revision 1.13  2001/02/28 16:58:19  ivm
# Added NB server example
#
# Revision 1.12  2000/11/16 21:20:05  ivm
# *** empty log message ***
#
# Revision 1.11  2000/10/02 15:21:17  ivm
# v1_9: do not setup python
#
# Revision 1.10  2000/09/05 18:25:53  ivm
# v1_8
#
# Revision 1.9  2000/09/05 18:25:24  ivm
# Do not register TCPServer until it's enabled
#
# Revision 1.8  2000/08/22 14:22:19  ivm
# Added serialize.com
#
# Revision 1.7  2000/07/25 17:29:36  ivm
# Do not use os.path module. It is unavailable in Python 1.5.1
#
# Revision 1.6  2000/07/10 14:09:26  ivm
# Added ABSTRACT
#
# Revision 1.5  2000/06/29 22:27:55  ivm
# Added time->string conversion to cvtime
#
# Revision 1.4  2000/06/23 15:40:11  ivm
# Implemented new format of relative time
#
# Revision 1.3  2000/06/04 17:54:15  ivm
# Added examples
#
# Revision 1.2  2000/05/15 20:51:52  ivm
# Use envRemove() instead of pathRemove()
#
# Revision 1.1  2000/04/25 18:09:58  ivm
# Added Makefile, UPS stuff
#
#

VERSION = v2_1a

LIBFILES = Parser.py      SockStream.py  config.py      futil.py \
	Selector.py    TCPServer.py   cvtime.py serialize.py
UPSFILES = fcslib.table
EXMFILES = examples/echo-client.py examples/echo-server.py examples/echo-nb-server.py

DSTROOT = ./dst-root
UPSDIR = $(DSTROOT)/ups
LIBDIR = $(DSTROOT)/lib
EXMDIR = $(DSTROOT)/examples
DIRS = $(UPSDIR) $(LIBDIR) $(EXMDIR)
TARFILE = /tmp/fcslib_$(VERSION).tar

upstar: $(DIRS)
	cp $(LIBFILES) $(LIBDIR)
	cd $(LIBDIR); chmod ugo+rx $(LIBFILES)
	cp $(UPSFILES) $(UPSDIR)
	cd $(UPSDIR); chmod ugo+rx $(UPSFILES)
	cp $(EXMFILES) $(EXMDIR)
	cp README ABSTRACT $(DSTROOT)
	chmod ugo+rx $(DSTROOT)/README
	cd $(DSTROOT);	tar cvf $(TARFILE) *
	rm -rf $(DSTROOT)
	@echo ""
	@echo $(TARFILE) is ready
	@echo ""

$(LIBDIR):
	mkdir -p $(LIBDIR)

$(EXMDIR):
	mkdir -p $(EXMDIR)

$(UPSDIR):
	mkdir -p $(UPSDIR)

$(DSTROOT):
	mkdir -p $(DSTROOT)
