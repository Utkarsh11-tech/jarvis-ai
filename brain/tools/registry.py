"""
JARVIS Tool Registry

Provides a small, explicit capability layer between the JARVIS brain and
existing execution code.

The registry is intentionally independent of any LLM so it can be tested
and used by the current command pipeline first.

System capabilities are also exposed through this registry, allowing future
LLM/tool routing to use the same capability interface.
"""

from dataclasses import dataclass
from typing import Any, Callable

from brain.tools.system_tools import (
    get_battery_status,
    get_cpu_usage,
    get_disk_usage,
    get_memory_usage,
    get_network_status,
    get_resource_summary,
    get_system_info,
    lock_computer,
    sleep_computer,
)

# ==========================================================
# TOOL DEFINITION
# ==========================================================


@dataclass(frozen=True)
class ToolDefinition:
    """Description of one capability available to JARVIS."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any]
    requires_confirmation: bool = False


# ==========================================================
# TOOL REGISTRY
# ==========================================================


class ToolRegistry:
    """Stores and resolves the capabilities available to JARVIS."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    # ======================================================
    # REGISTER
    # ======================================================

    def register(
        self,
        tool: ToolDefinition,
    ) -> None:
        """Register a tool by its unique name."""

        if not tool.name.strip():
            raise ValueError("Tool name cannot be empty.")

        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    # ======================================================
    # GET
    # ======================================================

    def get(
        self,
        name: str,
    ) -> ToolDefinition | None:
        """Return a registered tool, or None when it does not exist."""

        return self._tools.get(name)

    # ======================================================
    # REQUIRE
    # ======================================================

    def require(
        self,
        name: str,
    ) -> ToolDefinition:
        """Return a registered tool or raise a clear lookup error."""

        tool = self.get(name)

        if tool is None:
            raise KeyError(f"Unknown JARVIS tool: {name}")

        return tool

    # ======================================================
    # LIST
    # ======================================================

    def list_tools(
        self,
    ) -> list[ToolDefinition]:
        """Return tools in deterministic name order."""

        return [self._tools[name] for name in sorted(self._tools)]

    # ======================================================
    # DESCRIBE
    # ======================================================

    def describe(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return LLM-friendly tool metadata.

        Python handlers are deliberately excluded.
        """

        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "requires_confirmation": (tool.requires_confirmation),
            }
            for tool in self.list_tools()
        ]

    # ======================================================
    # INVOKE
    # ======================================================

    def invoke(
        self,
        name: str,
        **arguments: Any,
    ) -> Any:
        """
        Invoke a registered tool with keyword arguments.

        Confirmation policy is metadata only at this layer.
        The caller is responsible for enforcing confirmation
        before invoking tools marked as requiring it.
        """

        return self.require(name).handler(**arguments)


# ==========================================================
# EXISTING EXECUTOR ADAPTER
# ==========================================================


def _execute_intent(
    intent: str,
    target: str,
    **extra: Any,
) -> Any:
    """
    Adapt the existing executor to the new tool interface.
    """

    from brain.core.executor import execute

    command = {
        "intent": intent,
        "target": target,
        **extra,
    }

    return execute(command)


# ==========================================================
# EXISTING TOOL HANDLERS
# ==========================================================


def _open_application(
    target: str,
) -> Any:

    return _execute_intent(
        "OPEN_APPLICATION",
        target,
    )


def _play_media(
    target: str,
    profile_directory: str | None = None,
) -> Any:

    return _execute_intent(
        "PLAY_MEDIA",
        target,
        profile_directory=profile_directory,
    )


def _web_search(
    target: str,
) -> Any:

    return _execute_intent(
        "WEB_SEARCH",
        target,
    )


def _file_search(
    target: str,
) -> Any:

    return _execute_intent(
        "FILE_SEARCH",
        target,
    )


def _ui_automation() -> Any:

    return _execute_intent(
        "UI_AUTOMATION",
        "",
    )


def _system_command(
    target: str,
) -> Any:

    return _execute_intent(
        "SYSTEM_COMMAND",
        target,
    )


# ==========================================================
# DEFAULT REGISTRY
# ==========================================================


def get_default_registry() -> ToolRegistry:
    """
    Build the default JARVIS capability registry.

    Existing executor-backed capabilities are preserved.
    System capabilities are added alongside them.
    """

    registry = ToolRegistry()

    # ======================================================
    # EXISTING TOOLS
    # ======================================================

    registry.register(
        ToolDefinition(
            name="open_application",
            description=(
                "Open an installed application or " "resolve a matching local item."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                    },
                },
                "required": [
                    "target",
                ],
            },
            handler=_open_application,
        )
    )

    registry.register(
        ToolDefinition(
            name="play_media",
            description=(
                "Play requested media, optionally " "using a selected Chrome profile."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                    },
                    "profile_directory": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                },
                "required": [
                    "target",
                ],
            },
            handler=_play_media,
        )
    )

    registry.register(
        ToolDefinition(
            name="web_search",
            description=("Open a web search for the requested query."),
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                    },
                },
                "required": [
                    "target",
                ],
            },
            handler=_web_search,
        )
    )

    registry.register(
        ToolDefinition(
            name="file_search",
            description=(
                "Search the local filesystem for a " "file or folder by name."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                    },
                },
                "required": [
                    "target",
                ],
            },
            handler=_file_search,
        )
    )

    registry.register(
        ToolDefinition(
            name="ui_automation",
            description=("Run the existing JARVIS UI automation test flow."),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=_ui_automation,
        )
    )

    registry.register(
        ToolDefinition(
            name="system_command",
            description=(
                "Request a system shutdown or restart. "
                "This capability requires confirmation."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "enum": [
                            "shutdown",
                            "restart",
                        ],
                    },
                },
                "required": [
                    "target",
                ],
            },
            handler=_system_command,
            requires_confirmation=True,
        )
    )

    # ======================================================
    # SYSTEM INFORMATION
    # ======================================================

    registry.register(
        ToolDefinition(
            name="get_system_info",
            description=(
                "Get basic information about the "
                "current computer and operating system."
            ),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=get_system_info,
        )
    )

    # ======================================================
    # CPU
    # ======================================================

    registry.register(
        ToolDefinition(
            name="get_cpu_usage",
            description=("Get current CPU usage and processor information."),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=get_cpu_usage,
        )
    )

    # ======================================================
    # MEMORY
    # ======================================================

    registry.register(
        ToolDefinition(
            name="get_memory_usage",
            description=("Get current RAM usage and memory statistics."),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=get_memory_usage,
        )
    )

    # ======================================================
    # DISK
    # ======================================================

    registry.register(
        ToolDefinition(
            name="get_disk_usage",
            description=("Get storage usage for a local disk path."),
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                },
            },
            handler=get_disk_usage,
        )
    )

    # ======================================================
    # BATTERY
    # ======================================================

    registry.register(
        ToolDefinition(
            name="get_battery_status",
            description=(
                "Get battery percentage, charging state, "
                "and remaining battery information."
            ),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=get_battery_status,
        )
    )

    # ======================================================
    # NETWORK
    # ======================================================

    registry.register(
        ToolDefinition(
            name="get_network_status",
            description=(
                "Get information about the computer's " "local network interfaces."
            ),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=get_network_status,
        )
    )

    # ======================================================
    # RESOURCE SUMMARY
    # ======================================================

    registry.register(
        ToolDefinition(
            name="get_resource_summary",
            description=("Get a compact summary of CPU, memory, " "and disk usage."),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=get_resource_summary,
        )
    )

    # ======================================================
    # LOCK
    # ======================================================

    registry.register(
        ToolDefinition(
            name="lock_computer",
            description=("Lock the current Windows workstation."),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=lock_computer,
            requires_confirmation=False,
        )
    )

    # ======================================================
    # SLEEP
    # ======================================================

    registry.register(
        ToolDefinition(
            name="sleep_computer",
            description=(
                "Put the computer into sleep mode. "
                "This capability requires confirmation."
            ),
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=sleep_computer,
            requires_confirmation=True,
        )
    )

    return registry
