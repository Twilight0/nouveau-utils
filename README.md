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
sudo pacman -U nouveau-utils-2.2.0-1-any.pkg.tar.zst

# Or build locally
makepkg -sric
```

### Debian / Ubuntu / Pop!_OS / Linux Mint
```bash
sudo dpkg -i nouveau-utils_2.2.0-1_all.deb
sudo apt-get install -f
```

### Fedora / RHEL / openSUSE
```bash
sudo dnf install nouveau-utils-2.2.0-1.noarch.rpm
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
nouveau-ctrl auto
```

### TUI Dashboard (`nouveau-tui`)
```bash
nouveau-tui
```
* **Hotkeys:**
  - `0`-`3`: Lock to performance level (`0` = deep idle, `3` = max 3D).
  - `A`: Return to automatic governor mode.
  - `R`: Force reload telemetry and daemon configuration.
  - `Q` / `Esc`: Exit dashboard.

### Configuration
Edit `/etc/nouveau-dynclockd.conf` to configure polling intervals, PowerMizer hold timers, battery capping, and 120 Hz display floor protection. Custom per-application profiles can be placed in `/etc/nouveau-dynclockd.d/*.conf`.

---

## License

GPL-2.0-only
