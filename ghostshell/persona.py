"""Ghost Personality and Theme Engine for GhostShell (Phase 6).

Provides configurable supernatural personas that alter Gemma's commentary style
while keeping underlying technical guidance and bug fixes completely accurate.
All personality prompts are strictly injected into the system prompt, never as
untrusted user inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class GhostPersona:
    """Configuration and tone definitions for a ghost personality.

    Attributes:
        name: Short identifier used in CLI and configuration.
        title: Display name in the grimoire UI.
        tagline: One-sentence role summary.
        tone_description: Descriptive guide for developers.
        prompt_instruction: Injected into system prompt to guide style.
    """

    name: str
    title: str
    tagline: str
    tone_description: str
    prompt_instruction: str


# ==============================================================================
# The Three Spectral Archetypes
# ==============================================================================

ARCHIVIST_PROMPT: Final[str] = (
    "PERSONALITY ARCHETYPE: The Archivist.\n"
    "Tone: Reflective, solemn, mysterious, and historical. You view the codebase as an ancient scroll "
    "or digital fossil etched into silicon. You reference lost repositories, forgotten punch cards, "
    "and the passage of machine epochs. While maintaining this haunting, contemplative air, your technical "
    "diagnoses and code fixes must remain completely precise, modern, and actionable."
)

POLTERGEIST_PROMPT: Final[str] = (
    "PERSONALITY ARCHETYPE: The Poltergeist.\n"
    "Tone: Playful, mischievous, chaotic, and energetic. You love to haunt the terminal with supernatural "
    "pranks, flickers, and eerie laughter. You tease the developer about typos, runaway loops, and segfaults, "
    "yet you are genuinely helpful at heart. Deliver razor-sharp bug fixes laced with playful spectral antics. "
    "Never let humor obscure the exact technical correctness of your code."
)

GRIM_DEBUGGER_PROMPT: Final[str] = (
    "PERSONALITY ARCHETYPE: The Grim Debugger.\n"
    "Tone: Direct, technical, cynical, and deadpan. You are a weary, no-nonsense ghost who has seen every "
    "NullPointerException and off-by-one bug since 1970. You have zero patience for sloppy indentation or "
    "leaky abstractions, offering biting dry wit and surgical code repairs. Your technical advice is concise, "
    "uncompromising, and authoritative."
)


ARCHIVIST = GhostPersona(
    name="archivist",
    title="The Ancient Archivist",
    tagline="Keeper of lost commits, ancient punch-cards, and dusty machine lore.",
    tone_description="Reflective, solemn, and mysterious; frames programming questions through digital history.",
    prompt_instruction=ARCHIVIST_PROMPT,
)

POLTERGEIST = GhostPersona(
    name="poltergeist",
    title="The Mischievous Poltergeist",
    tagline="Sprightly spirit rattling pointers, flickering cursor lights, and teasing bugs.",
    tone_description="Playful, chaotic, and witty; teases coding errors while delivering accurate fixes.",
    prompt_instruction=POLTERGEIST_PROMPT,
)

GRIM_DEBUGGER = GhostPersona(
    name="grim-debugger",
    title="The Grim Debugger",
    tagline="Weary terminal apparition with dry cynical humor and surgical precision.",
    tone_description="Direct, technical, and deadpan; zero fluff, instant diagnosis.",
    prompt_instruction=GRIM_DEBUGGER_PROMPT,
)

AVAILABLE_PERSONAS: Final[dict[str, GhostPersona]] = {
    "archivist": ARCHIVIST,
    "poltergeist": POLTERGEIST,
    "grim-debugger": GRIM_DEBUGGER,
}

DEFAULT_PERSONA_NAME: Final[str] = "grim-debugger"


# ==============================================================================
# Theme Definitions
# ==============================================================================

@dataclass(frozen=True)
class GhostThemeColors:
    """Color palette for GhostShell terminal rendering."""

    name: str
    primary: str
    bright: str
    dim: str
    accent: str
    warn: str
    error: str
    text: str


AVAILABLE_THEMES: Final[dict[str, GhostThemeColors]] = {
    "green": GhostThemeColors(
        name="green",
        primary="#00FF66",
        bright="#39FF14",
        dim="#2D7D46",
        accent="#00F0FF",
        warn="#FFB000",
        error="#FF3366",
        text="#E0F8E8",
    ),
    "amber": GhostThemeColors(
        name="amber",
        primary="#FFB000",
        bright="#FFCC00",
        dim="#8B6508",
        accent="#FF8C00",
        warn="#FFD700",
        error="#FF4500",
        text="#FFF8DC",
    ),
    "cyan": GhostThemeColors(
        name="cyan",
        primary="#00F0FF",
        bright="#80FFFF",
        dim="#008080",
        accent="#00FF66",
        warn="#FFB000",
        error="#FF3366",
        text="#E6FFFF",
    ),
    "monochrome": GhostThemeColors(
        name="monochrome",
        primary="#E0E0E0",
        bright="#FFFFFF",
        dim="#707070",
        accent="#CCCCCC",
        warn="#FFFFFF",
        error="#FFFFFF",
        text="#F0F0F0",
    ),
}

DEFAULT_THEME_NAME: Final[str] = "green"


class PersonaEngine:
    """Manages active ghost personality and theme configurations."""

    def __init__(
        self,
        default_persona: str = DEFAULT_PERSONA_NAME,
        default_theme: str = DEFAULT_THEME_NAME,
    ) -> None:
        """Initialize the persona engine.

        Args:
            default_persona: Initial personality name ('archivist', 'poltergeist', or 'grim-debugger').
            default_theme: Initial theme name ('green', 'amber', 'cyan', 'monochrome').
        """
        self._persona = self._resolve_persona(default_persona)
        self._theme = self._resolve_theme(default_theme)

    @property
    def current_persona(self) -> GhostPersona:
        """Get the active GhostPersona."""
        return self._persona

    @property
    def current_theme(self) -> GhostThemeColors:
        """Get the active GhostThemeColors."""
        return self._theme

    def _resolve_persona(self, name: str) -> GhostPersona:
        """Resolve a persona by name or fallback to default."""
        cleaned = name.strip().lower()
        if cleaned in AVAILABLE_PERSONAS:
            return AVAILABLE_PERSONAS[cleaned]
        # Normalize aliases
        if cleaned in ("grim", "debugger", "grim_debugger"):
            return GRIM_DEBUGGER
        if cleaned in ("archive", "history"):
            return ARCHIVIST
        if cleaned in ("ghost", "polter", "chaos"):
            return POLTERGEIST
        return AVAILABLE_PERSONAS[DEFAULT_PERSONA_NAME]

    def _resolve_theme(self, name: str) -> GhostThemeColors:
        """Resolve a theme by name or fallback to default."""
        cleaned = name.strip().lower()
        if cleaned in AVAILABLE_THEMES:
            return AVAILABLE_THEMES[cleaned]
        return AVAILABLE_THEMES[DEFAULT_THEME_NAME]

    def set_persona(self, name: str) -> bool:
        """Change the active ghost personality.

        Args:
            name: One of 'archivist', 'poltergeist', 'grim-debugger'.

        Returns:
            True if the name was recognized and activated, False if unknown.
        """
        cleaned = name.strip().lower()
        if cleaned in AVAILABLE_PERSONAS or cleaned in (
            "grim", "debugger", "grim_debugger", "archive", "history", "ghost", "polter", "chaos"
        ):
            self._persona = self._resolve_persona(cleaned)
            return True
        return False

    def set_theme(self, name: str) -> bool:
        """Change the active color theme.

        Args:
            name: One of 'green', 'amber', 'cyan', 'monochrome'.

        Returns:
            True if recognized, False otherwise.
        """
        cleaned = name.strip().lower()
        if cleaned in AVAILABLE_THEMES:
            self._theme = AVAILABLE_THEMES[cleaned]
            return True
        return False

    def build_system_prompt(self, base_prompt: str) -> str:
        """Compose the full system prompt injecting the active personality.

        Ensures personality styling is added to the authoritative system prompt
        and never trusted user inputs.

        Args:
            base_prompt: The core GhostShell system instructions.

        Returns:
            Composite system prompt for local Gemma inference.
        """
        return (
            f"{base_prompt}\n\n"
            f"==============================================================================\n"
            f"{self._persona.prompt_instruction}\n"
            f"==============================================================================\n"
            f"CRITICAL REMINDER: Your technical answers, Java bug exorcisms, and code reviews "
            f"must remain strictly factual, practical, and syntactically correct despite your eerie persona."
        )
