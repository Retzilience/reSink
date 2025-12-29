# source/patchbay.py
from __future__ import annotations

import configparser
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import QMessageBox, QWidget

from config_store import ConfigStore


@dataclass(frozen=True)
class PatchbayChoice:
    kind: str  # "asyphon" | "qpwgraph" | "helvum" | "patchance" | "custom"
    argv: List[str]


def _windows_appdata_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata)
    home = Path.home()
    return home / "AppData" / "Roaming"


def _linux_xdg_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".config"


def _candidate_asyphon_cfg_paths() -> List[Path]:
    sysname = platform.system().lower()

    if sysname.startswith("windows"):
        base = _windows_appdata_dir()
    elif sysname.startswith("linux"):
        base = _linux_xdg_config_dir()
    else:
        base = Path.home() / ".config"

    dirs = ("aSyphon", "asyphon", "ASyphon")
    files = ("asyphon.cfg", "aSyphon.cfg")

    out: List[Path] = []
    for d in dirs:
        for fn in files:
            out.append(base / d / fn)
    return out


def _read_asyphon_last_exe_path(cfg_path: Path) -> str:
    try:
        cp = configparser.ConfigParser()
        cp.read(cfg_path, encoding="utf-8")
        return (cp.get("App", "last_exe_path", fallback="") or "").strip()
    except Exception:
        return ""


def _normalize_path(raw: str, *, relative_to: Path) -> Path:
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (relative_to / p).resolve()
    else:
        p = p.resolve()
    return p


def find_asyphon_launch_argv() -> Optional[List[str]]:
    """
    I locate aSyphon via its own config (asyphon.cfg) by reading [App] last_exe_path.
    If that path points to a .py file, I launch it with sys.executable.
    """
    for cfg_path in _candidate_asyphon_cfg_paths():
        if not cfg_path.exists():
            continue

        raw = _read_asyphon_last_exe_path(cfg_path)
        if not raw:
            continue

        p = _normalize_path(raw, relative_to=cfg_path.parent)
        if not p.exists():
            continue
        if not p.is_file():
            continue

        if p.suffix.lower() == ".py":
            return [sys.executable, str(p)]
        return [str(p)]

    return None


def resolve_patchbay_choice(store: ConfigStore) -> Optional[PatchbayChoice]:
    cfg = store.load()
    selected_app = (cfg.get("Patchbay", "selected_app", fallback="") or "").strip()
    custom_path = (cfg.get("Patchbay", "custom_path", fallback="") or "").strip()

    if not selected_app:
        return None

    if selected_app == "asyphon":
        argv = find_asyphon_launch_argv()
        if not argv:
            return None
        return PatchbayChoice(kind="asyphon", argv=argv)

    if selected_app in ("qpwgraph", "helvum", "patchance"):
        return PatchbayChoice(kind=selected_app, argv=[selected_app])

    if selected_app == "custom":
        if not custom_path:
            return None

        cmd = custom_path.strip()
        p = Path(cmd).expanduser()
        if p.exists() and p.is_file():
            return PatchbayChoice(kind="custom", argv=[str(p.resolve())])

        # I keep the old behavior for power users who typed a command string.
        return PatchbayChoice(kind="custom", argv=cmd.split())

    return None


def launch_patchbay(choice: PatchbayChoice, parent: QWidget) -> None:
    if not choice.argv or not (choice.argv[0] or "").strip():
        QMessageBox.critical(parent, "Patchbay", "Invalid patchbay command.")
        return

    try:
        subprocess.Popen(list(choice.argv), close_fds=True)
    except FileNotFoundError:
        QMessageBox.critical(parent, "Patchbay", f"Command not found:\n\n{choice.argv[0]}")
    except Exception as e:
        QMessageBox.critical(parent, "Patchbay", f"Failed to launch patchbay:\n\n{e}")
