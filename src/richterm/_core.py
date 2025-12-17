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
from rich.text import Text


@dataclass(slots=True)
class RenderOptions:
    """Options that control how a transcript is rendered."""

    prompt: str = "$"
    hide_command: bool = False


class CommandExecutionError(RuntimeError):
    """Raised when a command cannot be executed."""


_COLOR_ENV_DEFAULTS: dict[str, str] = {
    "FORCE_COLOR": "1",
    "CLICOLOR_FORCE": "1",
    "PY_COLORS": "1",
    "TTY_COMPATIBLE": "1",
}


def _prepare_environment(env: Mapping[str, str] | None) -> dict[str, str]:
    if os.environ.get("RICHTERM_DISABLE_COLOR_HINT", "0") == "1":
        return dict(env) if env is not None else os.environ.copy()

    env_vars = os.environ.copy()
    if env is not None:
        env_vars.update(env)

    term = env_vars.get("TERM", "")
    if not term or term == "dumb":
        env_vars["TERM"] = "xterm-256color"

    if "NO_COLOR" in env_vars:
        return env_vars

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

    return console.export_svg(title="")


def command_to_display(command: Sequence[str]) -> str:
    """Return a shell-like representation of *command* suitable for display."""

    return shlex.join(command)
