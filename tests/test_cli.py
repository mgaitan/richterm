from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path
from runpy import run_module

import pytest

from richterm import get_version, main


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
    svg = output_path.read_text(encoding="utf-8")
    assert "hidden" in svg
    assert "$ python" not in svg


def test_cli_non_zero_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_path = tmp_path / "failure.svg"
    exit_code = main(
        [
            "-o",
            str(output_path),
            "python",
            "-c",
            "import sys; sys.stderr.write('boom'); sys.exit(3)",
        ]
    )
    assert exit_code == 3
    captured = capsys.readouterr()
    assert captured.out.splitlines()[0] == "boom"
    assert output_path.exists()
    assert "boom" in output_path.read_text(encoding="utf-8")


def test_cli_command_not_found(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["this-command-should-not-exist-123456"])
    assert exit_code == 127
    captured = capsys.readouterr()
    assert "Command not found" in captured.err


def test_module_entry_point(mocker) -> None:
    mocker.patch.object(sys, "argv", ["richterm", "--version"])
    patched_main = mocker.patch("richterm.main", return_value=5)
    with pytest.raises(SystemExit) as excinfo:
        run_module("richterm.__main__", run_name="__main__")
    assert excinfo.value.code == 5
    patched_main.assert_called_once_with(["--version"])


def test_get_version_package_not_found(mocker) -> None:
    mocker.patch(
        "importlib.metadata.version",
        side_effect=metadata.PackageNotFoundError("not found"),
    )
    assert get_version() == "unknown"
