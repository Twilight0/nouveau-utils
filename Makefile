VERSION ?= 2.2.1
PKGNAME ?= nouveau-utils
DESTDIR ?=
PREFIX ?= /usr

all:
	@echo "Nouveau Userspace Governance & Telemetry Suite (v$(VERSION))"
	@echo "Available targets:"
	@echo "  make install  - Install binaries, configs, and service to DESTDIR"
	@echo "  make clean    - Clean build/packaging artifacts"

install:
	# Binaries
	install -Dm755 nouveau-ctrl $(DESTDIR)$(PREFIX)/bin/nouveau-ctrl
	install -Dm755 nouveau-tui $(DESTDIR)$(PREFIX)/bin/nouveau-tui
	install -Dm755 nouveau-dynclockd.py $(DESTDIR)$(PREFIX)/bin/nouveau-dynclockd.py
	ln -sf nouveau-dynclockd.py $(DESTDIR)$(PREFIX)/bin/nouveau-dynclockd
	
	# Configurations
	install -Dm644 nouveau-dynclockd.conf $(DESTDIR)/etc/nouveau-dynclockd.conf
	install -d $(DESTDIR)/etc/nouveau-dynclockd.d
	install -Dm644 apps.conf.sample $(DESTDIR)/etc/nouveau-dynclockd.d/apps.conf.sample
	
	# Systemd Service
	install -Dm644 nouveau-dynclockd.service $(DESTDIR)$(PREFIX)/lib/systemd/system/nouveau-dynclockd.service

clean:
	rm -rf *.pkg.tar.zst *.deb *.rpm build/ dist/

.PHONY: all install clean
