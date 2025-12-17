"""richterm - generate Rich-rendered transcripts of terminal commands."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from importlib import metadata
from pathlib import Path

from ._core import (
    CommandExecutionError,
    RenderOptions,
    command_to_display,
    render_svg,
    run_command,
)


def get_version() -> str:
    try:
        return metadata.version("richterm")
    except metadata.PackageNotFoundError:  # pragma: no cover - resolved at runtime when installed
        return "unknown"


def _default_output_path() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(f"rich_term_{timestamp}.svg")


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="richterm",
        description="Generate SVG transcripts of terminal commands rendered with Rich.",
        add_help=False,
    )
    parser.add_argument("-?", "--help", action="help", help="Show this help message and exit.")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {get_version()}")
    visibility = parser.add_mutually_exclusive_group()
    visibility.add_argument(
        "-h",
        "--hide-command",
        action="store_true",
        dest="hide_command",
        help="Do not include the command line in the generated transcript.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write the SVG transcript to this path (defaults to a timestamped file in the current directory).",
    )
    parser.add_argument(
        "--prompt",
        default="$",
        help="Prompt to display before the command. Accepts Rich markup.",
    )
    visibility.add_argument(
        "--shown-command",
        dest="shown_command",
        help="Override the command text shown in the transcript without changing the executed command.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute. Additional arguments are passed through verbatim.",
    )
    return parser


@dataclass(slots=True)
class CLIOptions:
    command: list[str]
    prompt: str
    hide_command: bool
    output: Path | None
    shown_command: str | None


def _parse_args(args: Sequence[str] | None) -> CLIOptions:
    parser = get_parser()
    parsed = parser.parse_args(args=args)
    if not parsed.command:
        parser.error("a command to execute is required")
    return CLIOptions(
        command=parsed.command,
        prompt=parsed.prompt,
        hide_command=parsed.hide_command,
        output=parsed.output,
        shown_command=parsed.shown_command,
    )


def main(args: Sequence[str] | None = None) -> int:
    """Entry point for the ``richterm`` command-line interface."""

    options = _parse_args(args)

    try:
        completed = run_command(options.command)
    except CommandExecutionError as exc:
        print(exc, file=sys.stderr)
        return 127

    output_path = options.output or _default_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    transcript = completed.stdout or ""
    command_display = None
    if not options.hide_command:
        command_display = options.shown_command or command_to_display(options.command)
    svg = render_svg(
        command_display,
        transcript,
        RenderOptions(prompt=options.prompt, hide_command=options.hide_command),
    )
    output_path.write_text(svg, encoding="utf-8")

    if transcript:
        sys.stdout.write(transcript)
        if not transcript.endswith("\n"):
            sys.stdout.write("\n")
    print(f"Created {output_path}")

    return completed.returncode


__all__ = ["RenderOptions", "command_to_display", "get_parser", "main", "render_svg", "run_command"]
