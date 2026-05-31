"""
M.I.L.O — Machine Intelligence Liaison Operator
src/tools/system_ops.py

Core system operations module.
Handles local task automation and routes results back to the Brain (Gemini API).
"""

from __future__ import annotations

import os
import platform
import subprocess
import shutil
import psutil
import datetime
import traceback
from pathlib import Path
from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# Result envelope
# ──────────────────────────────────────────────────────────────────────────────

class OperationResult:
    """Uniform return type for every system operation."""

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: str | None = None,
        raw_traceback: str | None = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.raw_traceback = raw_traceback

    def as_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "raw_traceback": self.raw_traceback,
        }

    @classmethod
    def ok(cls, data: Any = None) -> "OperationResult":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str, tb: str = "") -> "OperationResult":
        return cls(success=False, error=error, raw_traceback=tb)


# ──────────────────────────────────────────────────────────────────────────────
# Self-healing decorator
# ──────────────────────────────────────────────────────────────────────────────

def capture_errors(func):
    """
    Decorator that wraps any system operation.
    On exception, packages the full traceback into an OperationResult.fail()
    so the Brain (Gemini) can analyse it and propose a patch.
    """
    def wrapper(*args, **kwargs) -> OperationResult:
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            tb = traceback.format_exc()
            return OperationResult.fail(error=str(exc), tb=tb)
    wrapper.__name__ = func.__name__
    return wrapper


# ──────────────────────────────────────────────────────────────────────────────
# Application control
# ──────────────────────────────────────────────────────────────────────────────

class AppController:
    """Open and manage applications cross-platform."""

    # Map friendly names → platform-specific commands
    _APP_MAP: dict[str, dict[str, str]] = {
        "browser":    {"Windows": "start chrome",   "Darwin": "open -a 'Google Chrome'", "Linux": "google-chrome"},
        "vscode":     {"Windows": "code",            "Darwin": "code",                    "Linux": "code"},
        "terminal":   {"Windows": "start cmd",       "Darwin": "open -a Terminal",        "Linux": "x-terminal-emulator"},
        "calculator": {"Windows": "calc",            "Darwin": "open -a Calculator",      "Linux": "gnome-calculator"},
        "notepad":    {"Windows": "notepad",         "Darwin": "open -a TextEdit",        "Linux": "gedit"},
        "explorer":   {"Windows": "explorer",        "Darwin": "open .",                  "Linux": "nautilus ."},
    }

    @staticmethod
    @capture_errors
    def open_app(app_name: str) -> OperationResult:
        """Open a registered application by friendly name."""
        system = platform.system()
        key = app_name.lower().strip()
        entry = AppController._APP_MAP.get(key)

        if entry is None:
            # Attempt a raw launch as fallback
            cmd = app_name
        else:
            cmd = entry.get(system, "")
            if not cmd:
                return OperationResult.fail(f"No command defined for '{app_name}' on {system}.")

        subprocess.Popen(cmd, shell=True)
        return OperationResult.ok(data={"launched": app_name, "command": cmd})

    @staticmethod
    @capture_errors
    def list_running_processes() -> OperationResult:
        """Return a list of currently running process names."""
        procs = [p.info for p in psutil.process_iter(["pid", "name", "status"])]
        return OperationResult.ok(data=procs)

    @staticmethod
    @capture_errors
    def kill_process(name_or_pid: str | int) -> OperationResult:
        """Kill a process by name or PID."""
        killed = []
        for proc in psutil.process_iter(["pid", "name"]):
            match = (
                str(proc.info["pid"]) == str(name_or_pid)
                or proc.info["name"].lower() == str(name_or_pid).lower()
            )
            if match:
                proc.kill()
                killed.append(proc.info["name"])
        if not killed:
            return OperationResult.fail(f"No process found matching '{name_or_pid}'.")
        return OperationResult.ok(data={"killed": killed})


# ──────────────────────────────────────────────────────────────────────────────
# File management
# ──────────────────────────────────────────────────────────────────────────────

class FileManager:
    """Safe, sandboxed file system operations."""

    @staticmethod
    @capture_errors
    def list_directory(path: str = ".") -> OperationResult:
        p = Path(path).expanduser().resolve()
        if not p.is_dir():
            return OperationResult.fail(f"'{path}' is not a valid directory.")
        entries = [
            {"name": e.name, "type": "dir" if e.is_dir() else "file", "size_kb": round(e.stat().st_size / 1024, 2)}
            for e in sorted(p.iterdir())
        ]
        return OperationResult.ok(data={"path": str(p), "entries": entries})

    @staticmethod
    @capture_errors
    def read_file(path: str, max_bytes: int = 16_384) -> OperationResult:
        p = Path(path).expanduser().resolve()
        if not p.is_file():
            return OperationResult.fail(f"'{path}' is not a file.")
        content = p.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
        return OperationResult.ok(data={"path": str(p), "content": content})

    @staticmethod
    @capture_errors
    def write_file(path: str, content: str, overwrite: bool = False) -> OperationResult:
        p = Path(path).expanduser().resolve()
        if p.exists() and not overwrite:
            return OperationResult.fail(f"'{path}' already exists. Set overwrite=True to replace.")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return OperationResult.ok(data={"written": str(p)})

    @staticmethod
    @capture_errors
    def delete_file(path: str) -> OperationResult:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return OperationResult.fail(f"'{path}' does not exist.")
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return OperationResult.ok(data={"deleted": str(p)})

    @staticmethod
    @capture_errors
    def search_files(root: str, pattern: str) -> OperationResult:
        """Glob search for files matching a pattern."""
        p = Path(root).expanduser().resolve()
        matches = [str(f) for f in p.rglob(pattern)]
        return OperationResult.ok(data={"matches": matches, "count": len(matches)})


# ──────────────────────────────────────────────────────────────────────────────
# System status
# ──────────────────────────────────────────────────────────────────────────────

class SystemMonitor:
    """Hardware and OS telemetry."""

    @staticmethod
    @capture_errors
    def get_status() -> OperationResult:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        battery = psutil.sensors_battery()

        data = {
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total_gb": round(vm.total / 1e9, 2),
            "ram_used_percent": vm.percent,
            "disk_total_gb": round(disk.total / 1e9, 2),
            "disk_used_percent": disk.percent,
            "battery_percent": battery.percent if battery else "N/A",
            "plugged_in": battery.power_plugged if battery else "N/A",
            "uptime_hours": round((datetime.datetime.now().timestamp() - psutil.boot_time()) / 3600, 1),
        }
        return OperationResult.ok(data=data)

    @staticmethod
    @capture_errors
    def get_network_info() -> OperationResult:
        stats = psutil.net_io_counters()
        addrs = {iface: [a.address for a in addrs] for iface, addrs in psutil.net_if_addrs().items()}
        return OperationResult.ok(data={
            "interfaces": addrs,
            "bytes_sent_mb": round(stats.bytes_sent / 1e6, 2),
            "bytes_recv_mb": round(stats.bytes_recv / 1e6, 2),
        })


# ──────────────────────────────────────────────────────────────────────────────
# Shell executor (controlled)
# ──────────────────────────────────────────────────────────────────────────────

class ShellExecutor:
    """
    Run arbitrary shell commands with a hard timeout.
    Output (stdout + stderr) is returned as data so the Brain can inspect it.
    """

    @staticmethod
    @capture_errors
    def run(command: str, timeout: int = 15) -> OperationResult:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return OperationResult.ok(data={
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        })


# ──────────────────────────────────────────────────────────────────────────────
# Unified dispatcher — the single entry point M.I.L.O calls
# ──────────────────────────────────────────────────────────────────────────────

DISPATCH_TABLE: dict[str, callable] = {
    # Apps
    "open_app":              AppController.open_app,
    "list_processes":        AppController.list_running_processes,
    "kill_process":          AppController.kill_process,
    # Files
    "list_dir":              FileManager.list_directory,
    "read_file":             FileManager.read_file,
    "write_file":            FileManager.write_file,
    "delete_file":           FileManager.delete_file,
    "search_files":          FileManager.search_files,
    # System
    "system_status":         SystemMonitor.get_status,
    "network_info":          SystemMonitor.get_network_info,
    # Shell
    "shell_run":             ShellExecutor.run,
}


def execute(action: str, **kwargs) -> OperationResult:
    """
    Unified entry point.

    Usage:
        result = execute("open_app", app_name="vscode")
        result = execute("system_status")
        result = execute("write_file", path="~/notes.txt", content="hello")
    """
    handler = DISPATCH_TABLE.get(action)
    if handler is None:
        return OperationResult.fail(
            f"Unknown action '{action}'. "
            f"Available: {sorted(DISPATCH_TABLE.keys())}"
        )
    return handler(**kwargs)
