"""GhostShell - A spooky, local-first AI developer assistant.

Phase 3: Possessed Java Debugger integrated with local Gemma 3 1B
for the "Ghost in the Machine" open-source AI challenge.
"""

__version__ = "0.3.0"
__author__ = "GhostShell Team"
__challenge__ = "Ghost in the Machine"

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError
from ghostshell.commands import CommandAction, CommandDoc, CommandHandler, CommandResult
from ghostshell.config import GhostConfig, get_default_config
from ghostshell.debugger import JavaDebugger, JavaDebugRequest, JavaDebugResult
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
    "JavaDebugger",
    "JavaDebugRequest",
    "JavaDebugResult",
]
