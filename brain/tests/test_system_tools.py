"""
JARVIS System Tools Tests

Step 2A:
Validate the first offline system capability family.

These tests do not require:
    - XTTS
    - Ollama
    - RTX 5050
    - internet access
    - GUI startup
"""

import ast
import os

import pytest

from brain.tools.system_tools import (
    get_battery_status,
    get_cpu_usage,
    get_disk_usage,
    get_memory_usage,
    get_network_status,
    get_resource_summary,
    get_system_info,
    get_system_tool_handlers,
)

# ==========================================================
# TEST 1
# SYSTEM INFORMATION
# ==========================================================


def test_get_system_info():

    result = get_system_info()

    assert isinstance(
        result,
        dict,
    )

    expected_keys = {
        "system",
        "release",
        "version",
        "machine",
        "processor",
        "hostname",
        "python_version",
    }

    assert expected_keys.issubset(result.keys())

    assert result["system"]


# ==========================================================
# TEST 2
# CPU USAGE
# ==========================================================


def test_get_cpu_usage():

    pytest.importorskip("psutil")

    result = get_cpu_usage()

    assert isinstance(
        result,
        dict,
    )

    assert "percent" in result
    assert "logical_processors" in result
    assert "physical_processors" in result

    assert 0 <= result["percent"] <= 100

    assert result["logical_processors"] is None or result["logical_processors"] > 0


# ==========================================================
# TEST 3
# MEMORY USAGE
# ==========================================================


def test_get_memory_usage():

    pytest.importorskip("psutil")

    result = get_memory_usage()

    assert isinstance(
        result,
        dict,
    )

    assert result["total_bytes"] > 0
    assert result["used_bytes"] >= 0
    assert result["available_bytes"] >= 0

    assert 0 <= result["percent"] <= 100


# ==========================================================
# TEST 4
# DISK USAGE
# ==========================================================


def test_get_disk_usage():

    result = get_disk_usage()

    assert isinstance(
        result,
        dict,
    )

    assert "path" in result
    assert "total_bytes" in result
    assert "used_bytes" in result
    assert "free_bytes" in result
    assert "percent_used" in result

    assert result["total_bytes"] > 0
    assert result["used_bytes"] >= 0
    assert result["free_bytes"] >= 0

    assert 0 <= result["percent_used"] <= 100


# ==========================================================
# TEST 5
# CUSTOM DISK PATH
# ==========================================================


def test_get_disk_usage_custom_path(
    tmp_path,
):

    result = get_disk_usage(str(tmp_path))

    assert result["path"] == str(tmp_path)

    assert result["total_bytes"] > 0


# ==========================================================
# TEST 6
# BATTERY
# ==========================================================


def test_get_battery_status():

    pytest.importorskip("psutil")

    result = get_battery_status()

    assert isinstance(
        result,
        dict,
    )

    assert "available" in result
    assert "percent" in result
    assert "plugged" in result
    assert "seconds_left" in result

    assert isinstance(
        result["available"],
        bool,
    )

    if result["available"]:

        assert result["percent"] is None or 0 <= result["percent"] <= 100


# ==========================================================
# TEST 7
# NETWORK STATUS
# ==========================================================


def test_get_network_status():

    pytest.importorskip("psutil")

    result = get_network_status()

    assert isinstance(
        result,
        dict,
    )

    assert "interfaces" in result

    assert isinstance(
        result["interfaces"],
        dict,
    )


# ==========================================================
# TEST 8
# RESOURCE SUMMARY
# ==========================================================


def test_get_resource_summary():

    pytest.importorskip("psutil")

    result = get_resource_summary()

    assert isinstance(
        result,
        dict,
    )

    assert set(result.keys()) == {
        "cpu_percent",
        "memory_percent",
        "disk_percent",
    }

    assert 0 <= result["cpu_percent"] <= 100

    assert 0 <= result["memory_percent"] <= 100

    assert 0 <= result["disk_percent"] <= 100


# ==========================================================
# TEST 9
# HANDLER MAP
# ==========================================================


def test_system_tool_handlers():

    handlers = get_system_tool_handlers()

    expected_names = {
        "get_system_info",
        "get_cpu_usage",
        "get_memory_usage",
        "get_disk_usage",
        "get_battery_status",
        "get_network_status",
        "get_resource_summary",
        "lock_computer",
        "sleep_computer",
    }

    assert set(handlers.keys()) == expected_names

    for handler in handlers.values():

        assert callable(handler)


# ==========================================================
# TEST 10
# NO VOICE MODULE IMPORT
# ==========================================================


def test_system_tools_have_no_voice_import():

    import brain.tools.system_tools as system_tools

    module_path = system_tools.__file__

    assert module_path is not None

    with open(
        module_path,
        "r",
        encoding="utf-8",
    ) as file:

        source = file.read()

    tree = ast.parse(source)

    imported_modules = set()

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:
                imported_modules.add(alias.name)

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            if node.module:
                imported_modules.add(node.module)

    forbidden_modules = {
        "brain.voices",
        "brain.voices.voice_manager",
        "TTS",
        "TTS.api",
        "xtts",
        "xtts_v2",
    }

    for imported in imported_modules:

        assert imported not in (forbidden_modules)

        assert not imported.startswith("brain.voices.")


# ==========================================================
# TEST 11
# NO LLM MODULE IMPORT
# ==========================================================


def test_system_tools_have_no_llm_import():

    import brain.tools.system_tools as system_tools

    module_path = system_tools.__file__

    assert module_path is not None

    with open(
        module_path,
        "r",
        encoding="utf-8",
    ) as file:

        source = file.read()

    tree = ast.parse(source)

    imported_modules = set()

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:
                imported_modules.add(alias.name)

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            if node.module:
                imported_modules.add(node.module)

    forbidden_modules = {
        "ollama",
        "brain.models.ollama_client",
        "brain.models",
    }

    for imported in imported_modules:

        assert imported not in (forbidden_modules)

        assert not imported.startswith("brain.models.")


# ==========================================================
# TEST 12
# CURRENT PLATFORM
# ==========================================================


def test_current_platform_is_available():

    result = get_system_info()

    if os.name == "nt":

        assert result["system"] == ("Windows")
