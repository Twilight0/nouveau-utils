# nouveau-utils

**Userspace dynamic clock governor, CLI management utility, and interactive terminal dashboard for Nouveau GPU reclocking.**

Designed to accompany the [`nouveau-dkms`](https://github.com/Twilight0/nouveau-dkms) kernel driver to provide seamless automatic P-state scaling, zero-sudo telemetry monitoring, per-application profiles, and manual clock locking.

---

## Components

| Binary | Description |
| :--- | :--- |
| **`nouveau-dynclockd`** | Background system daemon monitoring hardware interrupt load, thermal conditions, high-refresh display state (120 Hz floor), and power source (AC/battery). |
| **`nouveau-ctrl`** | Non-root command-line interface for querying clocks, setting P-states, toggling auto governor mode, and inspecting VRAM/thermal metrics. |
| **`nouveau-tui`** | Real-time interactive curses terminal dashboard with live graphs, client process tracking, and instant P-state lock hotkeys. |
| **`nouveau-recover`** | Opt-in development/testing GPU wedged-runlist recovery (`99-nouveau-recover.rules` + `nouveau-recover.service`) triggered by `nouveau-dkms` `WEDGED=rebind` uevents; **disabled by default** (`AUTO_RECOVER=false`). Enable via `nouveau-ctrl recover enable` or `nouveau-tui` (`w`). |

---

## Requirements

* Linux kernel with [`nouveau-dkms`](https://github.com/Twilight0/nouveau-dkms) installed and loaded.
* Python 3.8+ (standard library only; no external pip dependencies required).
* Systemd (for `nouveau-dynclockd.service`).

---

## Installation

### Arch Linux / CachyOS / Manjaro
```bash
# Using prebuilt package
sudo pacman -U nouveau-utils-2.3.0-1-any.pkg.tar.zst

# Or from AUR
yay -S nouveau-utils

# Or build locally
makepkg -sric
```

### Debian / Ubuntu / Pop!_OS / Linux Mint
```bash
sudo dpkg -i nouveau-utils_2.3.0-1_all.deb
sudo apt-get install -f
```

### Fedora / RHEL / openSUSE
```bash
sudo dnf install nouveau-utils-2.3.0-1.noarch.rpm
```

### Manual Installation
```bash
sudo make install
sudo systemctl daemon-reload
sudo systemctl enable --now nouveau-dynclockd
```

---

## Usage

### CLI (`nouveau-ctrl`)
```bash
# Display live GPU telemetry (P-state, clocks, VRAM, thermals)
nouveau-ctrl status

# Show available P-states and hardware frequencies
nouveau-ctrl pstates

# Lock to performance state P0 (highest 3D clock) without stopping the daemon
nouveau-ctrl set 0f

# Return to automatic governor mode
nouveau-ctrl set auto

# Manage dev-only automatic wedged-GPU recovery (default: off)
nouveau-ctrl recover status
nouveau-ctrl recover enable     # Opt in: reload nouveau on WEDGED=rebind (stops desktop/DM)
nouveau-ctrl recover disable    # Return to safe default (off)
nouveau-ctrl recover now        # Trigger a one-shot manual GPU reload immediately
```

### TUI Dashboard (`nouveau-tui`)
```bash
nouveau-tui
```
* **Hotkeys:**
  - `Space` / `Enter`: Lock selected P-state or toggle dynamic governor.
  - `a`: Return to automatic governor mode.
  - `t` / `-` / `+`: Adjust thermal throttle threshold (50–95 °C).
  - `w`: Toggle dev-only automatic wedged-GPU recovery (`AUTO_RECOVER`).
  - `R`: Force reload daemon configuration (`SIGHUP`).
  - `q` / `Esc`: Exit dashboard.

### Configuration
Edit `/etc/nouveau-dynclockd.conf` to configure polling intervals, PowerMizer hold timers, battery capping, and 120 Hz display floor protection. Custom per-application profiles can be placed in `/etc/nouveau-dynclockd.d/*.conf`.

### Useful `nouveau-dkms` Kernel Module Options
Set these in `/etc/modprobe.d/nouveau.conf` (or `/usr/lib/modprobe.d/nouveau.conf`) to control how `nouveau-dynclockd` / `nouveau-ctrl` interact with the kernel driver:

| Option | Purpose for `nouveau-utils` |
|---|---|
| `vblank_continuous=1` | Keeps VBlank IRQs active on 120 Hz eDP panels and keeps `nouveau-dynclockd`'s display-mode floor guard reliable. |
| `config=NvFermiMemReclock=true` | Enables Fermi DDR3 memory reclocking when `nouveau-dynclockd` / `nouveau-ctrl` switches P-states. |
| `config=NvFermiSynthClocks=true` | Exposes board-verified synthetic P-states (`0a` intermediate and `10` OC, when defined in `quirks.h`) in debugfs `pstate`. |
| `config=NvFermiVblankSync=true` | Synchronizes Fermi DDR3 memory transitions to VBlank (default: `true`). |
| `config=NvClkMode=...` / `NvClkModeAC=...` / `NvClkModeDC=...` | Sets initial/fallback AC & DC P-states before `nouveau-dynclockd` starts (especially useful on Tesla & Kepler). |
| `config=NvBoost=0\|1\|2` | Controls kernel boost level on supported GPUs (relevant when extending `nouveau-utils` to Kepler). |
| `config=NvMemExec=false` | Dry-run safety mode for testing Tesla/Fermi/Kepler P-state switching without committing DRAM writes. |
| `runpm=0` | Disables runtime PM on Optimus laptops when debugging clocks continuously (otherwise `nouveau-utils` avoids waking suspended dGPUs). |
| `config=NvBios=<file>` | Loads a VBIOS image from `/lib/firmware` for testing without flashing EEPROM. |
| `drm.edid_firmware=<conn>:<file>` | Enables displays missing EDID EEPROMs (`nouveau-dkms` `v2.4.2+`) so `nouveau-dynclockd` detects the real refresh rate. |

---

## License

GPL-2.0-only
