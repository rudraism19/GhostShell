"""GhostShell - A spooky, local-first AI developer assistant.

Phase 2: Local Gemma 3 1B integration via llama.cpp server,
haunted terminal UI, and sandboxed developer assistance for the
"Ghost in the Machine" open-source AI challenge.
"""

__version__ = "0.2.0"
__author__ = "GhostShell Team"
__challenge__ = "Ghost in the Machine"

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError
from ghostshell.commands import CommandAction, CommandDoc, CommandHandler, CommandResult
from ghostshell.config import GhostConfig, get_default_config
from ghostshell.engine import BaseEngine, GemmaEngine, GhostResponse, PlaceholderEngine
from ghostshell.ui import GhostUI

__all__ = [
    "__version__",
    "GhostConfig",
    "get_default_config",
    "GhostUI",
    "CommandHandler",
    "CommandResult",
    "CommandAction",
    "CommandDoc",
    "BaseEngine",
    "GemmaEngine",
    "PlaceholderEngine",
    "GhostResponse",
    "GemmaClient",
    "CompletionResponse",
    "ModelServerError",
]
