Name:           nouveau-utils
Version:        2.2.0
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

%{!?_unitdir: %define _unitdir %{_prefix}/lib/systemd/system}

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
ln -sf nouveau-dynclockd.py %{buildroot}%{_bindir}/nouveau-dynclockd

# Configs
install -Dm644 %{SOURCE0} %{buildroot}%{_sysconfdir}/nouveau-dynclockd.conf
mkdir -p %{buildroot}%{_sysconfdir}/nouveau-dynclockd.d
install -Dm644 %{SOURCE5} %{buildroot}%{_sysconfdir}/nouveau-dynclockd.d/apps.conf.sample

# Systemd unit
install -Dm644 %{SOURCE2} %{buildroot}%{_unitdir}/nouveau-dynclockd.service

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
%{_unitdir}/nouveau-dynclockd.service
%config(noreplace) %{_sysconfdir}/nouveau-dynclockd.conf
%dir %{_sysconfdir}/nouveau-dynclockd.d
%{_sysconfdir}/nouveau-dynclockd.d/apps.conf.sample

%changelog
* Mon Oct 26 2026 Twilight0 <twilight0@vivaldi.net> - 2.2.0-1
- Initial release of standalone nouveau-utils.
