# Changelog

All notable changes to `nouveau-utils` are documented in this file.

## [2.3.0] - 2026-11-27

### Added
- **Opt-in wedged-GPU auto-recovery (`nouveau-recover`, `nouveau-recover.service`, `99-nouveau-recover.rules`)**: Responds to `WEDGED=rebind` uevents emitted by `nouveau-dkms` by stopping the display manager and DRM holders, unbinding `vtconsole`, reloading `nouveau` (with PCI unbind/rebind fallback), and restoring the desktop. **Disabled by default** (`AUTO_RECOVER=false`) because it is targeted at driver/Mesa development environments rather than regular users.
- **CLI recovery controls (`nouveau-ctrl recover`)**: Added `nouveau-ctrl recover [status|enable|disable|on|off|now]` and an `Auto-Recover` status line in `nouveau-ctrl status`.
- **TUI recovery visibility & toggle (`nouveau-tui`)**: Added `Auto-Recover (Dev)` status row in Tab 3 (Telemetry) and the `w` hotkey to toggle `/etc/nouveau-recover.conf`.
- **Tests & Documentation**: Added unit tests verifying default-off behavior and config toggling across `nouveau-recover`, `nouveau-ctrl`, and `nouveau-tui`; documented `nouveau-dkms` module options in `README.md`.

## [2.2.5] - 2026-11-24

### Fixed
- **Post-S3 suspend/resume reclocking stall (`nouveau-dynclockd.py`)**: After S3 resume, Nouveau's debugfs `pstate` node can report `info.pstate == -1` (omitting the `*` active-state marker), causing `get_current_pstate()` to return `None`. Removed the truthy guard (`if current_hardware_state and ...`) in both the manual lock and auto governor loops so `nouveau-dynclockd` re-applies the target pstate and restores hardware state tracking.
- **Tests**: Added `test_no_truthy_guard_on_current_hardware_state` regression test in `tests/test_nouveau_utils.py`.

## [2.2.4] - 2026-11-01

### Changed & Fixed
- Raise default `INTERRUPT_THRESHOLD` from `250` to `1000` IRQs/s to avoid false-positive DDR3 memory reclocking and PCIe link renegotiations during routine 2D desktop usage.
- Query active CRTC modes via debugfs atomic state instead of opening `/dev/dri/card0` on every polling tick.
- Add PCIe link protection (`init_pcie_link_protection`) and live config-space self-healing (`check_and_heal_pcie_config`) for BARs, MSI, Command register, and Fermi MSI edge latch (`0x704`).
- Decouple `nouveau-dkms` from hard `depends` to `optdepends` in Arch `PKGBUILD`.

## [2.2.3] - 2026-10-27

### Fixed
- De-bounce interrupt load detection on 120Hz/144Hz displays.

## [2.2.2] - 2026-10-26

### Changed
- Remove forced Blender state and allow pure dynamic governor scaling.

## [2.2.1] - 2026-10-26

### Changed
- Packaging and code separation.

## [2.2.0] - 2026-10-26

### Added
- Standalone `nouveau-utils` repository layout, zero-stutter vblank memory reclocking, zero-sudo governor, and packaging pipelines (Arch, Debian/Ubuntu, Fedora/RPM).
