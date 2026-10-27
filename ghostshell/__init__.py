"""GhostShell - The Terminal That Remembers.

A spooky, local-first AI developer assistant engineered for the
"Ghost in the Machine" open-source AI challenge.
"""

__version__ = "1.0.0"
__author__ = "GhostShell Team"
__challenge__ = "Ghost in the Machine"

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError
from ghostshell.commands import CommandAction, CommandDoc, CommandHandler, CommandResult
from ghostshell.config import GhostConfig, get_default_config, is_local_endpoint
from ghostshell.debugger import JavaDebugger, JavaDebugRequest, JavaDebugResult
from ghostshell.engine import BaseEngine, GemmaEngine, GhostResponse, PlaceholderEngine
from ghostshell.git_intel import GitCommit, GitIntelligence, GitReviewResult, GitStoryResult, GitWorkingTreeStatus
from ghostshell.memory import GhostMemory, MemoryEntry
from ghostshell.persona import AVAILABLE_PERSONAS, AVAILABLE_THEMES, GhostPersona, GhostThemeColors, PersonaEngine
from ghostshell.ui import GhostUI

__all__ = [
    "__version__",
    "GhostConfig",
    "get_default_config",
    "is_local_endpoint",
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
    "GitIntelligence",
    "GitCommit",
    "GitWorkingTreeStatus",
    "GitStoryResult",
    "GitReviewResult",
    "GhostMemory",
    "MemoryEntry",
    "GhostPersona",
    "GhostThemeColors",
    "PersonaEngine",
    "AVAILABLE_PERSONAS",
    "AVAILABLE_THEMES",
]
