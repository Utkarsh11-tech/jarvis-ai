"""
JARVIS Command Planner

Converts a natural-language command into one or more executable
intent/target dictionaries. This extracts the planning responsibility
from Assistant while preserving the existing command-processing behavior.
"""

from brain.core.normalizer import normalize
from brain.core.intent_detector import detect_intent
from brain.core.target_extractor import extract_target


class CommandPlanner:
    """Builds executable command plans from normalized user input."""

    def __init__(self, context=None):
        self.context = context

    def _resolve_reference(self, target):
        """Resolve a target through the existing context manager when available."""
        if self.context is None:
            return target
        return self.context.resolve_reference(target)

    @staticmethod
    def _split_commands(command):
        """Split sequential commands while preserving the existing JARVIS syntax."""
        return command.replace(" and then ", " and ").split(" and ")

    def plan(self, command):
        """Return the executable plan for a user command."""
        command = normalize(command)

        if not command:
            return []

        results = []

        for current_command in self._split_commands(command):
            words = current_command.split()

            if not words:
                continue

            action = words[0]
            target = extract_target(words)
            target = self._resolve_reference(target)
            intent = detect_intent(action, target)

            if intent == "SYSTEM_COMMAND" and not target:
                target = action

            result = {
                "intent": intent,
                "target": target,
            }

            results.append(result)

            if self.context is not None and target:
                self.context.remember(
                    intent=intent,
                    target=target,
                )

        return results


def plan_command(command, context=None):
    """Convenience wrapper for callers that do not need a planner instance."""
    return CommandPlanner(context).plan(command)
