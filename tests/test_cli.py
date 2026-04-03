from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path
from runpy import run_module

import pytest

from richterm import get_version, main

EXIT_STATUS_ERROR = 3
EXIT_STATUS_NOT_FOUND = 127
MODULE_EXIT_CODE = 5


def _normalize_svg(svg_text: str) -> str:
    # Replace Rich's non-breaking spaces to allow simple substring checks.
    return svg_text.replace("&#160;", " ")


def test_cli_requires_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main([])
    captured = capsys.readouterr()
    assert "a command to execute is required" in captured.err


def test_cli_runs_command_and_creates_svg(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_path = tmp_path / "example.svg"
    exit_code = main(["-o", str(output_path), "python", "-c", "print('hello', end='')"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "hello" in captured.out
    assert captured.out.strip().endswith(f"Created {output_path}")
    assert output_path.exists()
    svg = output_path.read_text(encoding="utf-8")
    assert "<svg" in svg and "hello" in svg


def test_cli_hide_command(tmp_path: Path) -> None:
    output_path = tmp_path / "no_command.svg"
    exit_code = main(
        [
            "-h",
            "--prompt",
            "[bold]$",
            "-o",
            str(output_path),
            "python",
            "-c",
            "print('hidden')",
        ]
    )
    assert exit_code == 0
    svg = _normalize_svg(output_path.read_text(encoding="utf-8"))
    assert "hidden" in svg
    assert "$ python" not in svg


def test_cli_shown_command_override(tmp_path: Path) -> None:
    output_path = tmp_path / "shown.svg"
    exit_code = main(
        [
            "--shown-command",
            "echo pretend",
            "-o",
            str(output_path),
            "python",
            "-c",
            "print('real')",
        ]
    )
    assert exit_code == 0
    svg = _normalize_svg(output_path.read_text(encoding="utf-8"))
    assert "real" in svg
    assert "echo pretend" in svg
    assert "python -c" not in svg


def test_cli_shown_command_rejects_hide_command() -> None:
    with pytest.raises(SystemExit):
        main(["--shown-command", "echo pretend", "--hide-command", "echo", "hi"])


def test_cli_theme_changes_svg_background(tmp_path: Path) -> None:
    output_path = tmp_path / "monokai.svg"
    exit_code = main(
        [
            "--theme",
            "monokai",
            "-o",
            str(output_path),
            "python",
            "-c",
            "print('hello')",
        ]
    )
    assert exit_code == 0
    svg = output_path.read_text(encoding="utf-8")
    assert 'fill="#0c0c0c"' in svg


def test_cli_theme_uses_environment_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("RICHTERM_THEME", "monokai")
    output_path = tmp_path / "env-theme.svg"
    exit_code = main(
        [
            "-o",
            str(output_path),
            "python",
            "-c",
            "print('hello')",
        ]
    )
    assert exit_code == 0
    svg = output_path.read_text(encoding="utf-8")
    assert 'fill="#0c0c0c"' in svg


def test_cli_theme_option_overrides_environment(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("RICHTERM_THEME", "monokai")
    output_path = tmp_path / "override-theme.svg"
    exit_code = main(
        [
            "--theme",
            "svg-export",
            "-o",
            str(output_path),
            "python",
            "-c",
            "print('hello')",
        ]
    )
    assert exit_code == 0
    svg = output_path.read_text(encoding="utf-8")
    assert 'fill="#292929"' in svg
    assert 'fill="#0c0c0c"' not in svg


def test_cli_rejects_unknown_theme(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--theme", "unknown-theme", "echo", "hello"])
    captured = capsys.readouterr()
    assert "Unknown theme 'unknown-theme'" in captured.err


def test_cli_rejects_unknown_theme_from_environment(capsys: pytest.CaptureFixture[str], monkeypatch) -> None:
    monkeypatch.setenv("RICHTERM_THEME", "unknown-theme")
    with pytest.raises(SystemExit):
        main(["echo", "hello"])
    captured = capsys.readouterr()
    assert "Unknown theme 'unknown-theme'" in captured.err


def test_cli_non_zero_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_path = tmp_path / "failure.svg"
    exit_code = main(
        [
            "-o",
            str(output_path),
            "python",
            "-c",
            f"import sys; sys.stderr.write('boom'); sys.exit({EXIT_STATUS_ERROR})",
        ]
    )
    assert exit_code == EXIT_STATUS_ERROR
    captured = capsys.readouterr()
    assert captured.out.splitlines()[0] == "boom"
    assert output_path.exists()
    assert "boom" in output_path.read_text(encoding="utf-8")


def test_cli_command_not_found(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["this-command-should-not-exist-123456"])
    assert exit_code == EXIT_STATUS_NOT_FOUND
    captured = capsys.readouterr()
    assert "Command not found" in captured.err


def test_module_entry_point(mocker) -> None:
    mocker.patch.object(sys, "argv", ["richterm", "--version"])
    patched_main = mocker.patch("richterm.main", return_value=MODULE_EXIT_CODE)
    with pytest.raises(SystemExit) as excinfo:
        run_module("richterm.__main__", run_name="__main__")
    assert excinfo.value.code == MODULE_EXIT_CODE
    patched_main.assert_called_once_with(["--version"])


def test_get_version_package_not_found(mocker) -> None:
    mocker.patch(
        "importlib.metadata.version",
        side_effect=metadata.PackageNotFoundError("not found"),
    )
    assert get_version() == "unknown"
