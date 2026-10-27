"""Unit tests for GhostShell personality and theme engine (Phase 6)."""

from __future__ import annotations

import pytest

from ghostshell.persona import (
    AVAILABLE_PERSONAS,
    AVAILABLE_THEMES,
    DEFAULT_PERSONA_NAME,
    DEFAULT_THEME_NAME,
    PersonaEngine,
)


def test_persona_initial_state() -> None:
    """Verify default persona and theme initialization."""
    engine = PersonaEngine()
    assert engine.current_persona.name == DEFAULT_PERSONA_NAME
    assert engine.current_theme.name == DEFAULT_THEME_NAME
    assert len(AVAILABLE_PERSONAS) == 3
    assert set(AVAILABLE_PERSONAS.keys()) == {"archivist", "poltergeist", "grim-debugger"}


def test_persona_switching() -> None:
    """Verify switching across all 3 archetypes."""
    engine = PersonaEngine()

    assert engine.set_persona("archivist") is True
    assert engine.current_persona.name == "archivist"
    assert "Archivist" in engine.current_persona.title

    assert engine.set_persona("poltergeist") is True
    assert engine.current_persona.name == "poltergeist"
    assert "Poltergeist" in engine.current_persona.title

    assert engine.set_persona("grim-debugger") is True
    assert engine.current_persona.name == "grim-debugger"
    assert "Grim Debugger" in engine.current_persona.title


def test_persona_alias_normalization() -> None:
    """Verify friendly aliases resolve to canonical personas."""
    engine = PersonaEngine()

    assert engine.set_persona("chaos") is True
    assert engine.current_persona.name == "poltergeist"

    assert engine.set_persona("history") is True
    assert engine.current_persona.name == "archivist"

    assert engine.set_persona("grim") is True
    assert engine.current_persona.name == "grim-debugger"


def test_persona_invalid_name() -> None:
    """Verify invalid persona name returns False and retains previous persona."""
    engine = PersonaEngine(default_persona="archivist")
    assert engine.current_persona.name == "archivist"

    assert engine.set_persona("vampire") is False
    assert engine.current_persona.name == "archivist"


def test_theme_switching() -> None:
    """Verify switching color themes across all supported palettes."""
    engine = PersonaEngine()

    for theme_name in ("amber", "cyan", "monochrome", "green"):
        assert engine.set_theme(theme_name) is True
        assert engine.current_theme.name == theme_name
        assert engine.current_theme.primary.startswith("#")

    assert engine.set_theme("neon-pink") is False
    assert engine.current_theme.name == "green"


def test_build_system_prompt_injection() -> None:
    """Verify active persona is injected into system prompt with technical reminder."""
    engine = PersonaEngine(default_persona="poltergeist")
    base_prompt = "You are a local developer assistant."
    composite = engine.build_system_prompt(base_prompt)

    assert base_prompt in composite
    assert "The Poltergeist" in composite
    assert "CRITICAL REMINDER" in composite
    assert "must remain strictly factual" in composite

    # Switch persona and verify dynamic system prompt changes
    engine.set_persona("archivist")
    composite_archivist = engine.build_system_prompt(base_prompt)
    assert "The Archivist" in composite_archivist
    assert "The Poltergeist" not in composite_archivist
