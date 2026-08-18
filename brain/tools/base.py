"""
JARVIS Tool Definitions

Defines the metadata contract for tools that JARVIS can use.

This module does not execute tools.
It only describes what a tool is and what permissions
or capabilities it requires.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional


class ToolRisk(str, Enum):
    """
    Risk classification for a JARVIS tool.

    SAFE:
        The tool can normally execute without confirmation.

    CONFIRMATION_REQUIRED:
        The tool should require explicit user confirmation
        before execution.

    RESTRICTED:
        The tool requires additional security handling and
        should not be executed automatically.
    """

    SAFE = "safe"
    CONFIRMATION_REQUIRED = "confirmation_required"
    RESTRICTED = "restricted"


@dataclass(frozen=True)
class ToolDefinition:
    """
    Describes one capability available to JARVIS.

    A ToolDefinition is metadata only. Actual execution logic
    can be attached through the optional handler.
    """

    name: str
    description: str
    category: str
    risk: ToolRisk = ToolRisk.SAFE
    requires_confirmation: bool = False
    handler: Optional[Callable[..., Any]] = None

    def __post_init__(self):
        """
        Validate the tool definition when it is created.
        """

        if not isinstance(self.name, str):
            raise TypeError("Tool name must be a string.")

        if not self.name.strip():
            raise ValueError("Tool name cannot be empty.")

        if not isinstance(self.description, str):
            raise TypeError("Tool description must be a string.")

        if not self.description.strip():
            raise ValueError("Tool description cannot be empty.")

        if not isinstance(self.category, str):
            raise TypeError("Tool category must be a string.")

        if not self.category.strip():
            raise ValueError("Tool category cannot be empty.")

        if not isinstance(self.risk, ToolRisk):
            raise TypeError("Tool risk must be a ToolRisk value.")

        if not isinstance(
            self.requires_confirmation,
            bool,
        ):
            raise TypeError("requires_confirmation must be a boolean.")

        if (
            self.risk == ToolRisk.CONFIRMATION_REQUIRED
            and not self.requires_confirmation
        ):
            raise ValueError(
                "Tools with confirmation-required risk "
                "must set requires_confirmation=True."
            )

        if self.risk == ToolRisk.SAFE and self.requires_confirmation:
            raise ValueError("SAFE tools cannot require confirmation.")

    def metadata(self) -> dict:
        """
        Return a serializable representation of the
        tool metadata.

        The handler itself is intentionally excluded because
        handlers are executable Python objects and should not
        be exposed as metadata.
        """

        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "risk": self.risk.value,
            "requires_confirmation": (self.requires_confirmation),
        }

    def execute(self, *args, **kwargs):
        """
        Execute the registered handler.

        A tool without a handler is a metadata-only tool and
        cannot currently be executed.
        """

        if self.handler is None:
            raise RuntimeError(f"Tool '{self.name}' has no execution handler.")

        return self.handler(
            *args,
            **kwargs,
        )
