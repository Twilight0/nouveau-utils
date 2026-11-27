VERSION ?= 2.3.1
PKGNAME ?= nouveau-utils
DESTDIR ?=
PREFIX ?= /usr

all:
	@echo "Nouveau Userspace Governance & Telemetry Suite (v$(VERSION))"
	@echo "Available targets:"
	@echo "  make check    - Run unit and integration test suite"
	@echo "  make install  - Install binaries, configs, and service to DESTDIR"
	@echo "  make clean    - Clean build/packaging artifacts"

check test:
	python3 -m unittest discover -s tests -v

install:
	# Binaries
	install -Dm755 nouveau-ctrl $(DESTDIR)$(PREFIX)/bin/nouveau-ctrl
	install -Dm755 nouveau-tui $(DESTDIR)$(PREFIX)/bin/nouveau-tui
	install -Dm755 nouveau-dynclockd.py $(DESTDIR)$(PREFIX)/bin/nouveau-dynclockd.py
	install -Dm755 nouveau-recover $(DESTDIR)$(PREFIX)/bin/nouveau-recover
	ln -sf nouveau-dynclockd.py $(DESTDIR)$(PREFIX)/bin/nouveau-dynclockd
	
	# Configurations
	install -Dm644 nouveau-dynclockd.conf $(DESTDIR)/etc/nouveau-dynclockd.conf
	install -d $(DESTDIR)/etc/nouveau-dynclockd.d
	install -Dm644 apps.conf.sample $(DESTDIR)/etc/nouveau-dynclockd.d/apps.conf.sample
	
	# Systemd Services & udev Rules
	install -Dm644 nouveau-dynclockd.service $(DESTDIR)$(PREFIX)/lib/systemd/system/nouveau-dynclockd.service
	install -Dm644 nouveau-recover.service $(DESTDIR)$(PREFIX)/lib/systemd/system/nouveau-recover.service
	install -Dm644 99-nouveau-recover.rules $(DESTDIR)$(PREFIX)/lib/udev/rules.d/99-nouveau-recover.rules

clean:
	rm -rf *.pkg.tar.zst *.deb *.rpm build/ dist/

.PHONY: all check test install clean
