Name:           nouveau-utils
Version:        2.3.1
Release:        1%{?dist}
Summary:        Userspace dynamic governor, CLI, and TUI for Nouveau
License:        GPL-2.0-only
URL:            https://github.com/Twilight0/nouveau-utils
Source0:        nouveau-dynclockd.conf
Source1:        nouveau-dynclockd.py
Source2:        nouveau-dynclockd.service
Source3:        nouveau-ctrl
Source4:        nouveau-tui
Source5:        apps.conf.sample
Source6:        nouveau-recover
Source7:        nouveau-recover.service
Source8:        99-nouveau-recover.rules

%{!?_unitdir: %define _unitdir %{_prefix}/lib/systemd/system}
%{!?_udevrulesdir: %define _udevrulesdir %{_prefix}/lib/udev/rules.d}

BuildArch:      noarch
Requires:       python3
Requires:       nouveau-dkms

%description
Userspace dynamic frequency governor, command-line management tool,
and interactive curses TUI for Nouveau GPU reclocking.

%install
rm -rf %{buildroot}

# Binaries
install -Dm755 %{SOURCE3} %{buildroot}%{_bindir}/nouveau-ctrl
install -Dm755 %{SOURCE4} %{buildroot}%{_bindir}/nouveau-tui
install -Dm755 %{SOURCE1} %{buildroot}%{_bindir}/nouveau-dynclockd.py
install -Dm755 %{SOURCE6} %{buildroot}%{_bindir}/nouveau-recover
ln -sf nouveau-dynclockd.py %{buildroot}%{_bindir}/nouveau-dynclockd

# Configs
install -Dm644 %{SOURCE0} %{buildroot}%{_sysconfdir}/nouveau-dynclockd.conf
mkdir -p %{buildroot}%{_sysconfdir}/nouveau-dynclockd.d
install -Dm644 %{SOURCE5} %{buildroot}%{_sysconfdir}/nouveau-dynclockd.d/apps.conf.sample

# Systemd units & udev rules
install -Dm644 %{SOURCE2} %{buildroot}%{_unitdir}/nouveau-dynclockd.service
install -Dm644 %{SOURCE7} %{buildroot}%{_unitdir}/nouveau-recover.service
install -Dm644 %{SOURCE8} %{buildroot}%{_udevrulesdir}/99-nouveau-recover.rules

%post
%systemd_post nouveau-dynclockd.service

%preun
%systemd_preun nouveau-dynclockd.service

%postun
%systemd_postun_with_restart nouveau-dynclockd.service

%files
%{_bindir}/nouveau-ctrl
%{_bindir}/nouveau-tui
%{_bindir}/nouveau-dynclockd.py
%{_bindir}/nouveau-dynclockd
%{_bindir}/nouveau-recover
%{_unitdir}/nouveau-dynclockd.service
%{_unitdir}/nouveau-recover.service
%{_udevrulesdir}/99-nouveau-recover.rules
%config(noreplace) %{_sysconfdir}/nouveau-dynclockd.conf
%dir %{_sysconfdir}/nouveau-dynclockd.d
%{_sysconfdir}/nouveau-dynclockd.d/apps.conf.sample

%changelog
* Fri Nov 27 2026 Twilight0 <twilight0@vivaldi.net> - 2.3.1-1
- Release v2.3.1: Skip PID 1 (systemd) and systemd-logind in nouveau-recover DRM teardown.

* Fri Nov 27 2026 Twilight0 <twilight0@vivaldi.net> - 2.3.0-1
- Release v2.3.0: Add opt-in dev-mode automatic wedged-GPU recovery (default: off).
- Add nouveau-recover helper, nouveau-recover.service, and 99-nouveau-recover.rules for WEDGED=rebind uevents.
- Expose auto-recover status and toggle in nouveau-ctrl (recover [status|enable|disable|now]) and nouveau-tui (hotkey 'w').

* Tue Nov 24 2026 Twilight0 <twilight0@vivaldi.net> - 2.2.5-1
- Release v2.2.5: Fix post-S3 resume reclocking stall when debugfs pstate lacks '*'.
- Re-apply target pstate in both manual lock and auto loops when get_current_pstate() returns None.

* Sun Nov 01 2026 Twilight0 <twilight0@vivaldi.net> - 2.2.4-1
- Release v2.2.4: PCIe link protection, CRTC debugfs polling, and reclocking de-bounce.
- Raise default INTERRUPT_THRESHOLD to 1000 IRQs/s to eliminate false memory reclocking.
- Avoid repetitive BAR1 flushes and VMM churn by polling CRTC state via debugfs.
- Add PCIe ASPM protection and live BAR/MSI auto-heal on link reset.

* Tue Oct 27 2026 Twilight0 <twilight0@vivaldi.net> - 2.2.3-1
- Release v2.2.3: De-bounce interrupt load detection on 120Hz/144Hz displays.
- Raise default INTERRUPT_THRESHOLD to 250 IRQs/s to eliminate false upclocks from idle VBlank interrupts.

* Mon Oct 26 2026 Twilight0 <twilight0@vivaldi.net> - 2.2.1-1
- Release v2.2.1: Packaging and code separation.
- Standalone release of userspace utilities.

* Mon Oct 26 2026 Twilight0 <twilight0@vivaldi.net> - 2.2.0-1
- Initial release of standalone nouveau-utils.
