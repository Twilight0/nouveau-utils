# Changelog

All notable changes to `nouveau-utils` are documented in this file.

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
