"""
JARVIS Capability View

Provides a read-only, LLM-safe view of the capabilities registered
with JARVIS.

This module does not:
    - execute tools
    - call Ollama
    - call XTTS
    - modify the registry
    - modify Assistant V2

Its only responsibility is converting the ToolRegistry into structured
capability information that can later be supplied to the LLM.
"""

from __future__ import annotations

from typing import Any

from brain.tools.registry import (
    ToolRegistry,
    get_default_registry,
)

# ==========================================================
# CAPABILITY SNAPSHOT
# ==========================================================


def get_capability_snapshot(
    registry: ToolRegistry,
) -> list[dict[str, Any]]:
    """
    Return a read-only capability snapshot.

    The returned data contains only information that is safe
    to expose to an LLM.

    Python handlers are never included.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    return registry.describe()


# ==========================================================
# DEFAULT CAPABILITY SNAPSHOT
# ==========================================================


def get_default_capability_snapshot() -> list[dict[str, Any]]:
    """
    Build the default JARVIS registry and return its
    LLM-safe capability description.
    """

    registry = get_default_registry()

    return get_capability_snapshot(registry)


# ==========================================================
# CAPABILITY NAMES
# ==========================================================


def get_capability_names(
    registry: ToolRegistry,
) -> list[str]:
    """
    Return the names of all registered capabilities.

    Names are returned in deterministic order.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    return [capability["name"] for capability in registry.describe()]


# ==========================================================
# CAPABILITY LOOKUP
# ==========================================================


def get_capability(
    registry: ToolRegistry,
    name: str,
) -> dict[str, Any] | None:
    """
    Return the LLM-safe description of one capability.

    Returns None when the capability does not exist.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    if not isinstance(
        name,
        str,
    ):
        raise TypeError("Capability name must be a string.")

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("Capability name cannot be empty.")

    for capability in registry.describe():

        if capability["name"] == normalized_name:
            return capability

    return None


# ==========================================================
# CONFIRMATION-REQUIRED CAPABILITIES
# ==========================================================


def get_confirmation_required_capabilities(
    registry: ToolRegistry,
) -> list[dict[str, Any]]:
    """
    Return capabilities that require explicit confirmation.

    This is metadata only.

    No tool is executed by this function.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    return [
        capability
        for capability in registry.describe()
        if capability["requires_confirmation"]
    ]


# ==========================================================
# SAFE CAPABILITIES
# ==========================================================


def get_safe_capabilities(
    registry: ToolRegistry,
) -> list[dict[str, Any]]:
    """
    Return capabilities that do not require confirmation.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    return [
        capability
        for capability in registry.describe()
        if not capability["requires_confirmation"]
    ]


# ==========================================================
# SERIALIZABLE CAPABILITY DOCUMENT
# ==========================================================


def build_capability_document(
    registry: ToolRegistry,
) -> dict[str, Any]:
    """
    Build the structured capability document that will
    eventually be supplied to the LLM.

    This is deliberately a plain Python dictionary so the
    next stage can serialize it as JSON or embed it into a
    system prompt without changing the registry.
    """

    if not isinstance(
        registry,
        ToolRegistry,
    ):
        raise TypeError("registry must be a ToolRegistry instance.")

    capabilities = get_capability_snapshot(registry)

    return {
        "name": "JARVIS",
        "capability_count": len(capabilities),
        "capabilities": capabilities,
    }


# ==========================================================
# DEFAULT CAPABILITY DOCUMENT
# ==========================================================


def build_default_capability_document() -> dict[str, Any]:
    """
    Build the capability document from the default registry.
    """

    registry = get_default_registry()

    return build_capability_document(registry)
