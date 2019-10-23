
VERSION = v3_0

LIBFILES = Parser.py      SockStream.py  config.py      futil.py \
	Selector.py    TCPServer.py   cvtime.py serialize.py __init__.py
UPSFILES = fcslib.table
EXMFILES = examples/echo-client.py examples/echo-server.py examples/echo-nb-server.py

DSTROOT = ./dst-root
UPSDIR = $(DSTROOT)/ups
LIBDIR = $(DSTROOT)/lib
EXMDIR = $(DSTROOT)/examples
DIRS = $(UPSDIR) $(LIBDIR) $(EXMDIR)
TARFILE = /tmp/fcslib_$(VERSION).tar

all: clean upstar
	
clean:
	rm -rf $(DSTROOT)

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
