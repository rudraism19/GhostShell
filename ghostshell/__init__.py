"""GhostShell - A spooky, local-first AI developer assistant.

Phase 1: Terminal UI, command handling, and placeholder response engine
for the "Ghost in the Machine" open-source AI challenge.
"""

__version__ = "0.1.0"
__author__ = "GhostShell Team"
__challenge__ = "Ghost in the Machine"

from ghostshell.config import GhostConfig, get_default_config
from ghostshell.ui import GhostUI
from ghostshell.commands import CommandHandler, CommandResult, CommandAction
from ghostshell.engine import PlaceholderEngine, GhostResponse

__all__ = [
    "__version__",
    "GhostConfig",
    "get_default_config",
    "GhostUI",
    "CommandHandler",
    "CommandResult",
    "CommandAction",
    "PlaceholderEngine",
    "GhostResponse",
]
