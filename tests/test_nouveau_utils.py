#!/usr/bin/env python3
"""
Unit & Integration Test Suite for nouveau-utils:
  - nouveau-dynclockd.py (Governor state machine, 120Hz floor, PCIe self-healing, profiles, telemetry)
  - nouveau-ctrl         (P-state/VRAM parser, unprivileged snapshot reader, CLI status)
  - nouveau-tui          (AST/compile check, telemetry & P-state parsing)
"""
import ast
import importlib.machinery
import importlib.util
import os
import py_compile
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SAMPLE_PSTATE = """03: core 50 MHz shader 101 MHz memory 324 MHz
07: core 202 MHz shader 405 MHz memory 324 MHz AC DC *
0f: core 590 MHz shader 1180 MHz memory 900 MHz
10: core 700 MHz shader 1400 MHz memory 900 MHz
AC: core 202 MHz shader 405 MHz memory 324 MHz
VRAM: 312 MiB / 3072 MiB used
"""

SAMPLE_CLIENTS = """             command  tgid dev master a   uid      magic
             Xorg      912   0   y    y     0          0
         cinnamon     1140   0   n    y  1000          0
          vkcube      4821   0   n    y  1000          0
"""

SAMPLE_DRM_STATE_120HZ = """crtc[0]: head-0
\tenable=1
\tactive=1
\tmode: "1920x1080": 120 396360 1920 1968 2000 2080 1080 1083 1088 1350 0x48 0x9
crtc[1]: head-1
\tenable=0
\tactive=0
"""

SAMPLE_DRM_STATE_60HZ = """crtc[0]: head-0
\tenable=1
\tactive=1
\tmode: "1920x1080": 60 133000 1920 1968 2000 2080 1080 1083 1088 1120 0x48 0x9
"""


def load_script_module(name, filename):
    path = os.path.join(REPO_ROOT, filename)
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class TestSyntaxAndArchitectureGuards(unittest.TestCase):
    """Verifies syntax, bytecode compilation, and regression invariants across all scripts."""

    def test_bytecode_compile_all_scripts(self):
        for script in ("nouveau-dynclockd.py", "nouveau-ctrl", "nouveau-tui"):
            path = os.path.join(REPO_ROOT, script)
            self.assertTrue(os.path.isfile(path), f"Missing {script}")
            with tempfile.NamedTemporaryFile(suffix=".pyc") as tmp:
                py_compile.compile(path, cfile=tmp.name, doraise=True)

    def test_no_card0_open_in_display_polling(self):
        """Regression test (v2.2.4): get_active_display_info must never open /dev/dri/card0."""
        path = os.path.join(REPO_ROOT, "nouveau-dynclockd.py")
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "get_active_display_info":
                calls = [
                    ast.unparse(sub.func)
                    for sub in ast.walk(node)
                    if isinstance(sub, ast.Call)
                ]
                self.assertNotIn("os.open", calls)
                self.assertNotIn("fcntl.ioctl", calls)

    def test_no_truthy_guard_on_current_hardware_state(self):
        """Regression test (v2.2.5): None from get_current_pstate() (post-S3 missing '*') must still call set_pstate()."""
        path = os.path.join(REPO_ROOT, "nouveau-dynclockd.py")
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("if current_hardware_state and current_hardware_state != target_state:", src)
        self.assertEqual(src.count("if current_hardware_state != target_state:"), 2)


class TestGovernorLogic(unittest.TestCase):
    """Tests nouveau-dynclockd.py functions using isolated temporary filesystems."""

    @classmethod
    def setUpClass(cls):
        cls.dyn = load_script_module("nouveau_dynclockd", "nouveau-dynclockd.py")

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="nouveau-utils-test.")
        self.dyn.config = dict(self.dyn.DEFAULT_CONFIG)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_default_interrupt_threshold_regression(self):
        """Regression test (v2.2.4): INTERRUPT_THRESHOLD must be >= 1000 to ignore 120Hz VBlank IRQs."""
        self.assertGreaterEqual(self.dyn.DEFAULT_CONFIG["INTERRUPT_THRESHOLD"], 1000)

    def test_desktop_client_classification(self):
        for desktop_app in ("Xorg", "Xwayland", "cinnamon", "kwin_wayland", "vivaldi-bin", "mpv", "csd-power"):
            self.assertTrue(self.dyn.is_desktop_client(desktop_app), f"{desktop_app} should be desktop client")
        for game_app in ("vkcube", "glmark2", "furmark", "csgo_linux64", "rpcs3"):
            self.assertFalse(self.dyn.is_desktop_client(game_app), f"{game_app} should NOT be desktop client")

    def test_load_config_and_profiles(self):
        cfg_file = os.path.join(self.tmpdir, "nouveau-dynclockd.conf")
        prof_dir = os.path.join(self.tmpdir, "nouveau-dynclockd.d")
        os.makedirs(prof_dir, exist_ok=True)

        with open(cfg_file, "w") as f:
            f.write(
                f"THROTTLE_TEMP=78\n"
                f"THROTTLE_HYST=6\n"
                f"POLL_INTERVAL=0.5\n"
                f"IDLE_STATE=03\n"
                f"BATTERY_CAP=false\n"
                f"DISPLAY_120HZ_FLOOR=true\n"
                f"ALLOW_OC_10=true\n"
                f"INTERRUPT_THRESHOLD=1200\n"
                f"PROFILES_DIR={prof_dir}\n"
            )
        with open(os.path.join(prof_dir, "custom.conf"), "w") as f:
            f.write("[apps]\nblender = 10\nsuperTuxKart = 0f\nmpv = 07\ninvalid_app = 99\n")

        with mock.patch.object(self.dyn, "CONFIG_PATH", cfg_file):
            cfg = self.dyn.load_config()
            self.assertEqual(cfg["THROTTLE_TEMP"], 78)
            self.assertEqual(cfg["THROTTLE_HYST"], 6)
            self.assertEqual(cfg["POLL_INTERVAL"], 0.5)
            self.assertFalse(cfg["BATTERY_CAP"])
            self.assertTrue(cfg["ALLOW_OC_10"])
            self.assertEqual(cfg["INTERRUPT_THRESHOLD"], 1200)
            self.assertEqual(self.dyn.app_profiles.get("blender"), "10")
            self.assertEqual(self.dyn.app_profiles.get("superTuxKart"), "0f")
            self.assertNotIn("invalid_app", self.dyn.app_profiles)

    def test_120hz_display_floor_and_debugfs_state_parsing(self):
        dpms_file = os.path.join(self.tmpdir, "dpms")
        state_file = os.path.join(self.tmpdir, "state")
        with open(dpms_file, "w") as f:
            f.write("On\n")
        with open(state_file, "w") as f:
            f.write(SAMPLE_DRM_STATE_120HZ)

        orig_exists = os.path.exists
        orig_open = open

        def fake_exists(p):
            if p == "/sys/kernel/debug/dri/0/state":
                return True
            return orig_exists(p)

        def fake_open(p, *args, **kwargs):
            if p == "/sys/kernel/debug/dri/0/state":
                return orig_open(state_file, *args, **kwargs)
            return orig_open(p, *args, **kwargs)

        with mock.patch("glob.glob", return_value=[dpms_file]), \
             mock.patch("os.path.exists", side_effect=fake_exists), \
             mock.patch("builtins.open", side_effect=fake_open):
            clk, ref, active = self.dyn.get_active_display_info()
            self.assertTrue(active)
            self.assertEqual(ref, 120)
            self.assertEqual(clk, 396360)
            self.assertEqual(self.dyn.get_effective_idle_state((clk, ref, active)), "07")

        # Now test 60 Hz low pixel clock -> drops to 03
        with open(state_file, "w") as f:
            f.write(SAMPLE_DRM_STATE_60HZ)
        with mock.patch("glob.glob", return_value=[dpms_file]), \
             mock.patch("os.path.exists", side_effect=fake_exists), \
             mock.patch("builtins.open", side_effect=fake_open):
            clk, ref, active = self.dyn.get_active_display_info()
            self.assertEqual(ref, 60)
            self.assertEqual(clk, 133000)
            self.assertEqual(self.dyn.get_effective_idle_state((clk, ref, active)), "03")

        # Now test DPMS Off at 120 Hz -> drops to 03
        self.assertEqual(self.dyn.get_effective_idle_state((396360, 120, False)), "03")

    def test_pcie_aspm_protection_and_live_bar_msi_self_healing(self):
        """Verifies PCIe link protection snapshot and live BAR/MSI/Command/0x704 self-healing."""
        pci_dir = os.path.join(self.tmpdir, "0000:01:00.0")
        link_dir = os.path.join(pci_dir, "link")
        os.makedirs(link_dir, exist_ok=True)

        for node in ("l1_aspm", "l0s_aspm", "clkpm"):
            with open(os.path.join(link_dir, node), "w") as f:
                f.write("1\n")

        res_file = os.path.join(pci_dir, "resource")
        with open(res_file, "w") as f:
            f.write(
                "0x00000000f0000000 0x00000000f1ffffff 0x0000000000040200\n"
                "0x00000000c0000000 0x00000000cfffffff 0x000000000014220c\n"
                "0x0000000000000000 0x0000000000000000 0x0000000000000000\n"
                "0x00000000d0000000 0x00000000d1ffffff 0x000000000014220c\n"
                "0x0000000000000000 0x0000000000000000 0x0000000000000000\n"
                "0x0000000000002000 0x000000000000207f 0x0000000000040101\n"
            )

        cfg_file = os.path.join(pci_dir, "config")
        cfg_buf = bytearray(2048)
        struct.pack_into("<H", cfg_buf, 0x04, 0x0407)
        struct.pack_into("<I", cfg_buf, 0x10, 0xF0000000)
        struct.pack_into("<HIIH", cfg_buf, 0x6A, 0x0081, 0xFEE07000, 0x00000000, 0x0021)
        with open(cfg_file, "wb") as f:
            f.write(cfg_buf)

        orig_exists = os.path.exists
        orig_open = open

        def redirect_pci(path):
            prefix = "/sys/bus/pci/devices/"
            if isinstance(path, str) and path.startswith(prefix):
                return os.path.join(self.tmpdir, path[len(prefix):])
            return path

        with mock.patch("os.path.exists", side_effect=lambda p: orig_exists(redirect_pci(p))), \
             mock.patch("builtins.open", side_effect=lambda p, *a, **kw: orig_open(redirect_pci(p), *a, **kw)):
            self.dyn.init_pcie_link_protection()

            # Verify ASPM nodes were disabled ("0")
            for node in ("l1_aspm", "l0s_aspm", "clkpm"):
                with orig_open(os.path.join(link_dir, node), "r") as f:
                    self.assertEqual(f.read().strip(), "0")

            # Healthy config should NOT trigger heal
            self.assertFalse(self.dyn.check_and_heal_pcie_config())

            # Simulate PCIe hot reset wiping Command (0x04) and BAR0..BAR5 (0x10..0x24)
            wiped = bytearray(2048)
            with orig_open(cfg_file, "wb") as f:
                f.write(wiped)

            # Now check_and_heal_pcie_config() must detect and restore live!
            self.assertTrue(self.dyn.check_and_heal_pcie_config())

            with orig_open(cfg_file, "rb") as f:
                healed = f.read(2048)
            cmd = struct.unpack_from("<H", healed, 0x04)[0]
            bars = struct.unpack_from("<6I", healed, 0x10)
            msi_ctrl, msi_lo, msi_hi, msi_data = struct.unpack_from("<HIIH", healed, 0x6A)
            self.assertEqual(cmd, 0x0407)
            self.assertEqual(bars[0], 0xF0000000)
            self.assertEqual(bars[1], 0xC000000C)
            self.assertEqual(bars[3], 0xD000000C)
            self.assertEqual(bars[5], 0x00002001)
            self.assertEqual(msi_ctrl & 0x1, 1)
            self.assertEqual(msi_lo, 0xFEE07000)
            self.assertEqual(msi_data, 0x0021)
            self.assertEqual(healed[0x704], 0xFF)

    def test_telemetry_snapshots_and_manual_lock(self):
        snap_dir = os.path.join(self.tmpdir, "run_nouveau")
        pstate_node = os.path.join(self.tmpdir, "pstate")
        clients_node = os.path.join(self.tmpdir, "clients")
        with open(pstate_node, "w") as f:
            f.write(SAMPLE_PSTATE)
        with open(clients_node, "w") as f:
            f.write(SAMPLE_CLIENTS)

        with mock.patch.object(self.dyn, "SNAPSHOT_DIR", snap_dir), \
             mock.patch.object(self.dyn, "PSTATE_SNAPSHOT", os.path.join(snap_dir, "pstate")), \
             mock.patch.object(self.dyn, "CLIENTS_SNAPSHOT", os.path.join(snap_dir, "clients")), \
             mock.patch.object(self.dyn, "VRAM_SNAPSHOT", os.path.join(snap_dir, "vram")), \
             mock.patch.object(self.dyn, "STATUS_SNAPSHOT", os.path.join(snap_dir, "status")), \
             mock.patch.object(self.dyn, "MODE_PATH", os.path.join(snap_dir, "mode")), \
             mock.patch.object(self.dyn, "active_pstate_path", pstate_node), \
             mock.patch.object(self.dyn, "active_clients_path", clients_node):

            self.assertEqual(self.dyn.get_current_pstate(), "07")
            used_mib, total_mib = self.dyn.read_pstate_vram()
            self.assertEqual(used_mib, 312.0)
            self.assertEqual(total_mib, 3072)

            self.dyn.publish_runtime_telemetry({"mode": "auto", "active_pstate": "07"})
            self.assertTrue(os.path.isfile(os.path.join(snap_dir, "pstate")))
            self.assertTrue(os.path.isfile(os.path.join(snap_dir, "vram")))
            self.assertIsNone(self.dyn.read_manual_lock())

            with open(os.path.join(snap_dir, "mode"), "w") as f:
                f.write("locked:0f\n")
            self.assertEqual(self.dyn.read_manual_lock(), "0f")


class TestNouveauCtrlParser(unittest.TestCase):
    """Tests nouveau-ctrl P-state parser and CLI execution."""

    @classmethod
    def setUpClass(cls):
        cls.ctrl = load_script_module("nouveau_ctrl", "nouveau-ctrl")

    def test_parse_pstates_data(self):
        with mock.patch.object(self.ctrl, "read_privileged_file", return_value=SAMPLE_PSTATE):
            states, active_id, live_clock = self.ctrl.get_pstates_data()
            self.assertEqual(active_id, "07")
            self.assertIn("03", states)
            self.assertIn("07", states)
            self.assertIn("0f", states)
            self.assertIn("10", states)
            self.assertEqual(states["0f"]["core"], 590)
            self.assertEqual(states["0f"]["shader"], 1180)
            self.assertEqual(states["0f"]["memory"], 900)
            self.assertEqual(live_clock["core"], 202)
            self.assertEqual(live_clock["memory"], 324)

    def test_cli_help(self):
        res = subprocess.run(
            [sys.executable, os.path.join(REPO_ROOT, "nouveau-ctrl"), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("nouveau-ctrl", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
