"""Unit tests for GhostShell configuration and security invariants."""

from __future__ import annotations

import os
import pytest
from rich.console import Console

from ghostshell.config import (
    ALLOW_COMMAND_EXECUTION,
    DEFAULT_MODEL_ENDPOINT,
    DEFAULT_MODEL_NAME,
    PHOSPHOR_BRIGHT,
    PHOSPHOR_GREEN,
    SPECTRAL_CYAN,
    GhostConfig,
    create_console,
    get_default_config,
)


def test_default_config() -> None:
    """Verify default configuration attributes and security settings."""
    config = get_default_config()
    assert config.app_name == "GhostShell"
    assert config.version == "0.3.0"
    assert config.allow_command_execution is False
    assert config.startup_animation is True
    assert config.model_endpoint == "http://127.0.0.1:9931/v1/chat/completions"
    assert config.model_name == DEFAULT_MODEL_NAME
    assert "ghostshell" in config.prompt_text


def test_security_invariant_immutable() -> None:
    """Ensure allow_command_execution cannot be modified to True."""
    config = GhostConfig()
    assert config.allow_command_execution is False

    with pytest.raises(ValueError, match="Security Violation"):
        config.allow_command_execution = True  # type: ignore[misc]

    assert config.allow_command_execution is False
    assert ALLOW_COMMAND_EXECUTION is False


def test_model_config_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify environment variables override model settings."""
    monkeypatch.setenv("GHOSTSHELL_MODEL_ENDPOINT", "http://127.0.0.1:9999/v1/chat/completions")
    monkeypatch.setenv("GHOSTSHELL_MODEL_NAME", "custom-gemma-3")
    monkeypatch.setenv("GHOSTSHELL_MODEL_TIMEOUT", "60.0")

    config = get_default_config()
    assert config.model_endpoint == "http://127.0.0.1:9999/v1/chat/completions"
    assert config.model_name == "custom-gemma-3"
    assert config.model_timeout == 60.0


def test_no_animation_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure GHOSTSHELL_NO_ANIMATION env var sets startup_animation to False."""
    monkeypatch.setenv("GHOSTSHELL_NO_ANIMATION", "1")
    config = get_default_config()
    assert config.startup_animation is False

    monkeypatch.setenv("GHOSTSHELL_NO_ANIMATION", "true")
    config2 = get_default_config()
    assert config2.startup_animation is False

    monkeypatch.delenv("GHOSTSHELL_NO_ANIMATION", raising=False)
    config3 = get_default_config()
    assert config3.startup_animation is True


def test_create_console() -> None:
    """Verify console creation and theme binding."""
    console = create_console()
    assert isinstance(console, Console)
    assert str(console.get_style("ghost.primary")) == "bold #00ff66"
    assert "bold" in str(console.get_style("ghost.bright"))
    assert "bold" in str(console.get_style("ghost.error"))


def test_color_constants() -> None:
    """Verify defined color hex strings."""
    assert PHOSPHOR_GREEN.startswith("#")
    assert PHOSPHOR_BRIGHT.startswith("#")
    assert SPECTRAL_CYAN.startswith("#")
