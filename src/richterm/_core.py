"""Core utilities for generating Rich-rendered terminal transcripts."""

from __future__ import annotations

import os
import shlex
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from subprocess import CompletedProcess

from rich.console import Console
from rich.terminal_theme import (
    DEFAULT_TERMINAL_THEME,
    DIMMED_MONOKAI,
    MONOKAI,
    NIGHT_OWLISH,
    SVG_EXPORT_THEME,
    TerminalTheme,
)
from rich.text import Text


@dataclass(slots=True)
class RenderOptions:
    """Options that control how a transcript is rendered."""

    prompt: str = "$"
    hide_command: bool = False
    theme: str = "default"


class CommandExecutionError(RuntimeError):
    """Raised when a command cannot be executed."""


class InvalidThemeError(ValueError):
    """Raised when a requested terminal theme is not supported."""

    def __init__(self, theme: str, available_themes: Sequence[str]) -> None:
        self.theme = theme
        self.available_themes = tuple(available_themes)
        available = ", ".join(self.available_themes)
        super().__init__(f"Unknown theme '{theme}'. Available themes: {available}")


_COLOR_ENV_DEFAULTS: dict[str, str] = {
    "FORCE_COLOR": "1",
    "CLICOLOR_FORCE": "1",
    "PY_COLORS": "1",
    "TTY_COMPATIBLE": "1",
}

_TERMINAL_THEMES: dict[str, TerminalTheme] = {
    "default": SVG_EXPORT_THEME,
    "light": DEFAULT_TERMINAL_THEME,
    "monokai": MONOKAI,
    "dimmed-monokai": DIMMED_MONOKAI,
    "night-owlish": NIGHT_OWLISH,
    "svg-export": SVG_EXPORT_THEME,
}


def available_terminal_themes() -> tuple[str, ...]:
    """Return the supported terminal theme names."""

    return tuple(_TERMINAL_THEMES)


def default_terminal_theme_name(env: Mapping[str, str] | None = None) -> str:
    """Return the default terminal theme name from *env* or the built-in fallback."""

    env_vars = os.environ if env is None else env
    return env_vars.get("RICHTERM_THEME", "default")


def normalize_terminal_theme(theme: str) -> str:
    """Return a canonical theme name or raise if it is unsupported."""

    normalized = theme.strip().lower().replace("_", "-")
    if normalized in _TERMINAL_THEMES:
        return normalized

    raise InvalidThemeError(theme, available_terminal_themes())


def get_terminal_theme(theme: str) -> TerminalTheme:
    """Resolve *theme* to a Rich terminal theme."""

    return _TERMINAL_THEMES[normalize_terminal_theme(theme)]


def _prepare_environment(env: Mapping[str, str] | None) -> dict[str, str]:
    if os.environ.get("RICHTERM_DISABLE_COLOR_HINT", "0") == "1":
        return dict(env) if env is not None else os.environ.copy()

    env_vars = os.environ.copy()
    if env is not None:
        env_vars.update(env)

    def _is_truthy(value: str | None) -> bool:
        return value not in {None, "", "0", "false", "False"}

    term = env_vars.get("TERM", "")
    if not term or term == "dumb":
        env_vars["TERM"] = "xterm-256color"

    color_requested = any(_is_truthy(env_vars.get(key)) for key in _COLOR_ENV_DEFAULTS)
    if "NO_COLOR" in env_vars and not color_requested:
        return env_vars

    if color_requested:
        env_vars.pop("NO_COLOR", None)

    for key, value in _COLOR_ENV_DEFAULTS.items():
        env_vars.setdefault(key, value)

    return env_vars


def run_command(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> CompletedProcess[str]:
    """Execute *command* and return the completed process.

    The standard output and standard error streams are merged so that
    ordering is preserved. ANSI escape sequences are captured verbatim.
    """

    try:
        env_vars = _prepare_environment(env)
        return subprocess.run(
            command,
            check=False,
            cwd=str(cwd) if cwd is not None else None,
            env=env_vars,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:  # pragma: no cover - exercised via CommandExecutionError
        raise CommandExecutionError(f"Command not found: {command[0] if command else '<empty>'}") from exc  # noqa: TRY003


def render_svg(command_display: str | None, output: str, options: RenderOptions) -> str:
    """Render *output* to SVG, optionally prefixed by *command_display*."""

    console = Console(record=True, file=StringIO())

    if not options.hide_command and command_display:
        prompt_text = Text.from_markup(options.prompt)
        prompt_text.append(" ")
        prompt_text.append(command_display)
        console.print(prompt_text)

    if output:
        console.print(Text.from_ansi(output), end="")

    return console.export_svg(title="", theme=get_terminal_theme(options.theme))


def command_to_display(command: Sequence[str]) -> str:
    """Return a shell-like representation of *command* suitable for display."""

    return shlex.join(command)
