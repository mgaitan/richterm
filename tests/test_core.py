from __future__ import annotations

from subprocess import CompletedProcess

import pytest

from richterm import _default_output_path
from richterm._core import (
    CommandExecutionError,
    RenderOptions,
    _prepare_environment,
    command_to_display,
    render_svg,
    run_command,
)


def test_command_to_display_quotes_arguments() -> None:
    assert command_to_display(["echo", "hello world"]) == "echo 'hello world'"


def test_render_svg_includes_prompt_and_command() -> None:
    svg = render_svg("echo hi", "hi\n", RenderOptions(prompt="[bold]$"))
    assert "<svg" in svg
    assert "echo" in svg and "hi" in svg
    assert "$" in svg


def test_render_svg_hides_command_when_requested() -> None:
    svg = render_svg("echo hi", "hi\n", RenderOptions(prompt="$", hide_command=True))
    assert "echo hi" not in svg
    assert "hi" in svg


def test_run_command_raises_for_missing_binary() -> None:
    with pytest.raises(CommandExecutionError):
        run_command(["this-command-should-not-exist-654321"])


def test_default_output_path_format(monkeypatch) -> None:
    path = _default_output_path()
    assert path.name.startswith("rich_term_")
    assert path.suffix == ".svg"


def test_run_command_sets_colorful_environment(mocker) -> None:
    completed = CompletedProcess(args=["echo"], returncode=0, stdout="")
    mock_run = mocker.patch("richterm._core.subprocess.run", return_value=completed)
    run_command(["echo", "hi"])
    env = mock_run.call_args.kwargs["env"]
    assert env.get("FORCE_COLOR") == "1"
    assert env.get("CLICOLOR_FORCE") == "1"
    assert env.get("PY_COLORS") == "1"
    assert env.get("TTY_COMPATIBLE") == "1"


def test_prepare_environment_disable_hint(monkeypatch) -> None:
    monkeypatch.setenv("RICHTERM_DISABLE_COLOR_HINT", "1")
    result = _prepare_environment({"EXAMPLE": "1"})
    assert result == {"EXAMPLE": "1"}
    monkeypatch.delenv("RICHTERM_DISABLE_COLOR_HINT", raising=False)


def test_prepare_environment_sets_term(monkeypatch) -> None:
    monkeypatch.delenv("RICHTERM_DISABLE_COLOR_HINT", raising=False)
    monkeypatch.delenv("TERM", raising=False)
    env = _prepare_environment(None)
    assert env["TERM"] == "xterm-256color"


def test_prepare_environment_respects_no_color(monkeypatch) -> None:
    monkeypatch.delenv("RICHTERM_DISABLE_COLOR_HINT", raising=False)
    for key in ("FORCE_COLOR", "CLICOLOR_FORCE", "PY_COLORS", "TTY_COMPATIBLE"):
        monkeypatch.delenv(key, raising=False)
    env = _prepare_environment({"NO_COLOR": "1"})
    assert env["NO_COLOR"] == "1"
    for key in ("FORCE_COLOR", "CLICOLOR_FORCE", "PY_COLORS", "TTY_COMPATIBLE"):
        assert key not in env


def test_prepare_environment_allows_forced_color(monkeypatch) -> None:
    monkeypatch.delenv("RICHTERM_DISABLE_COLOR_HINT", raising=False)
    env = _prepare_environment({"NO_COLOR": "1", "FORCE_COLOR": "1"})
    assert "NO_COLOR" not in env
    assert env["FORCE_COLOR"] == "1"
    assert env["CLICOLOR_FORCE"] == "1"
    assert env["PY_COLORS"] == "1"
    assert env["TTY_COMPATIBLE"] == "1"
