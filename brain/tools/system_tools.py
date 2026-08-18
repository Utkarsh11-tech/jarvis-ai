"""
JARVIS System Tools

Offline computer/system capabilities.

These tools intentionally avoid the LLM, XTTS, browser, and network.
They provide small, deterministic operations that can later be exposed
through the JARVIS Tool Registry.

Safety rules:
    - Read-only system information is safe.
    - Locking the workstation is considered safe.
    - Sleep requires confirmation.
    - Shutdown/restart remain handled by the existing confirmation flow.
    - Permanent file deletion is not implemented here.
"""

from __future__ import annotations

import ctypes
import os
import platform
import shutil
import subprocess
from typing import Any

# ==========================================================
# SYSTEM INFORMATION
# ==========================================================


def get_system_info() -> dict[str, Any]:
    """
    Return basic information about the current computer.
    """

    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


# ==========================================================
# CPU
# ==========================================================


def get_cpu_usage() -> dict[str, Any]:
    """
    Return CPU usage information.

    Uses psutil when available.

    psutil is imported lazily so importing this module does not
    immediately require the dependency.
    """

    try:
        import psutil
    except ImportError as error:
        raise RuntimeError("psutil is required for CPU usage information.") from error

    return {
        "percent": psutil.cpu_percent(interval=0.1),
        "logical_processors": psutil.cpu_count(logical=True),
        "physical_processors": psutil.cpu_count(logical=False),
    }


# ==========================================================
# MEMORY
# ==========================================================


def get_memory_usage() -> dict[str, Any]:
    """
    Return RAM usage information.
    """

    try:
        import psutil
    except ImportError as error:
        raise RuntimeError(
            "psutil is required for memory usage information."
        ) from error

    memory = psutil.virtual_memory()

    return {
        "total_bytes": memory.total,
        "available_bytes": memory.available,
        "used_bytes": memory.used,
        "percent": memory.percent,
    }


# ==========================================================
# DISK
# ==========================================================


def get_disk_usage(
    path: str | None = None,
) -> dict[str, Any]:
    """
    Return disk usage information.

    Defaults to the current system drive on Windows.
    """

    if path is None:

        if os.name == "nt":
            path = os.environ.get(
                "SystemDrive",
                "C:",
            )

        else:
            path = "/"

    usage = shutil.disk_usage(path)

    percent = usage.used / usage.total * 100 if usage.total else 0.0

    return {
        "path": path,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "percent_used": round(
            percent,
            2,
        ),
    }


# ==========================================================
# BATTERY
# ==========================================================


def get_battery_status() -> dict[str, Any]:
    """
    Return battery information.

    Raises RuntimeError when the current machine does not expose
    battery information.
    """

    try:
        import psutil
    except ImportError as error:
        raise RuntimeError("psutil is required for battery information.") from error

    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available": False,
            "percent": None,
            "plugged": None,
            "seconds_left": None,
        }

    return {
        "available": True,
        "percent": battery.percent,
        "plugged": battery.power_plugged,
        "seconds_left": battery.secsleft,
    }


# ==========================================================
# NETWORK STATUS
# ==========================================================


def get_network_status() -> dict[str, Any]:
    """
    Return local network-interface information.

    This does not perform an internet request.
    """

    try:
        import psutil
    except ImportError as error:
        raise RuntimeError("psutil is required for network information.") from error

    interfaces = psutil.net_if_addrs()

    result: dict[str, Any] = {}

    for interface_name, addresses in interfaces.items():

        result[interface_name] = []

        for address in addresses:

            result[interface_name].append(
                {
                    "family": str(address.family),
                    "address": address.address,
                    "netmask": address.netmask,
                }
            )

    return {
        "interfaces": result,
    }


# ==========================================================
# LOCK COMPUTER
# ==========================================================


def lock_computer() -> str:
    """
    Lock the current Windows workstation.

    This operation does not delete data or terminate applications.
    """

    if os.name != "nt":
        raise RuntimeError(
            "Locking the workstation is currently supported " "only on Windows."
        )

    result = ctypes.windll.user32.LockWorkStation()

    if result == 0:
        raise RuntimeError("Windows could not lock the workstation.")

    return "Computer locked."


# ==========================================================
# SLEEP COMPUTER
# ==========================================================


def sleep_computer() -> str:
    """
    Request Windows sleep.

    This function is intentionally kept separate from the
    existing Assistant V2 confirmation mechanism.

    The caller must decide whether user confirmation is required
    before invoking this function.
    """

    if os.name != "nt":
        raise RuntimeError(
            "Sleeping the computer is currently supported " "only on Windows."
        )

    subprocess.Popen(
        [
            "rundll32.exe",
            "powrprof.dll,SetSuspendState",
            "0",
            "1",
            "0",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return "Putting the computer to sleep."


# ==========================================================
# CPU / MEMORY / DISK SUMMARY
# ==========================================================


def get_resource_summary() -> dict[str, Any]:
    """
    Return a compact system-resource summary.
    """

    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()

    return {
        "cpu_percent": cpu["percent"],
        "memory_percent": memory["percent"],
        "disk_percent": disk["percent_used"],
    }


# ==========================================================
# DEFAULT SYSTEM TOOL MAP
# ==========================================================


def get_system_tool_handlers() -> dict[str, Any]:
    """
    Return the system capability handlers.

    This is intentionally separate from ToolRegistry registration.
    """

    return {
        "get_system_info": get_system_info,
        "get_cpu_usage": get_cpu_usage,
        "get_memory_usage": get_memory_usage,
        "get_disk_usage": get_disk_usage,
        "get_battery_status": get_battery_status,
        "get_network_status": get_network_status,
        "get_resource_summary": get_resource_summary,
        "lock_computer": lock_computer,
        "sleep_computer": sleep_computer,
    }
