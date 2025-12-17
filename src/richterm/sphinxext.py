"""Sphinx extension providing the ``richterm`` directive."""

from __future__ import annotations

import shlex
from collections.abc import Callable
from types import SimpleNamespace
from typing import ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.errors import SphinxError

from . import get_version
from ._core import CommandExecutionError, RenderOptions, command_to_display, render_svg, run_command


class RichTermDirective(Directive):
    """Directive that renders command output as an inline SVG."""

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec: ClassVar[dict[str, Callable[[str | None], object]]] = {
        "prompt": directives.unchanged,
        "hide-command": directives.flag,
    }
    has_content = False

    def _get_config(self) -> SimpleNamespace:
        env = getattr(self.state.document.settings, "env", None)
        if env is None:
            return SimpleNamespace(richterm_prompt="$", richterm_hide_command=False)
        config = getattr(env, "config", None)
        prompt = getattr(config, "richterm_prompt", "$")
        hide = getattr(config, "richterm_hide_command", False)
        return SimpleNamespace(richterm_prompt=prompt, richterm_hide_command=hide)

    def run(self) -> list[nodes.Node]:
        raw_command = self.arguments[0].strip()
        if not raw_command:
            raise self.severe("richterm directive requires a command to execute")  # noqa: TRY003

        config = self._get_config()
        prompt = self.options.get("prompt", config.richterm_prompt)
        hide_command = "hide-command" in self.options or bool(config.richterm_hide_command)

        try:
            command = shlex.split(raw_command)
        except ValueError as exc:
            raise self.severe(f"Failed to parse command: {exc}") from exc  # noqa: TRY003

        try:
            completed = run_command(command)
        except CommandExecutionError as exc:
            raise self.severe(str(exc)) from exc

        transcript = completed.stdout or ""
        svg = render_svg(
            command_to_display(command) if not hide_command else None,
            transcript,
            RenderOptions(prompt=prompt, hide_command=hide_command),
        )

        raw_node = nodes.raw("", svg, format="html")

        if completed.returncode != 0:
            raise SphinxError(  # noqa: TRY003
                f"Command '{command_to_display(command)}' exited with status {completed.returncode}"
            )

        return [raw_node]


def setup(app: Sphinx) -> dict[str, object]:
    app.add_config_value("richterm_prompt", "$", "env")
    app.add_config_value("richterm_hide_command", False, "env")
    app.add_directive("richterm", RichTermDirective)
    return {
        "version": get_version(),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
