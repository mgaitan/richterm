from __future__ import annotations

from types import SimpleNamespace

import pytest

try:  # pragma: no cover - optional dependency
    from docutils.frontend import OptionParser
    from docutils.parsers.rst import DirectiveError, Parser
    from docutils.utils import new_document
except ModuleNotFoundError:  # pragma: no cover - handled by pytest skip
    pytest.skip("docutils is required", allow_module_level=True)

try:  # pragma: no cover - optional dependency
    from sphinx.errors import SphinxError
except ModuleNotFoundError:  # pragma: no cover - handled by pytest skip
    pytest.skip("sphinx is required", allow_module_level=True)

from richterm import get_version
from richterm._core import CommandExecutionError
from richterm.sphinxext import RichTermDirective, setup


class DummyState:
    def __init__(self, document):
        self.document = document
        self.reporter = document.reporter


class DummyStateMachine:
    def __init__(self, document):
        self.document = document
        self.reporter = document.reporter


def _normalize_svg(svg_text: str) -> str:
    return svg_text.replace("&#160;", " ")


def make_directive(  # noqa: PLR0913
    command: str,
    *,
    prompt: str | None = None,
    hide_option: bool = False,
    config_prompt: str = "$",
    config_hide: bool = False,
    shown_command: str | None = None,
    config_shown: str | None = None,
    with_env: bool = True,
    builder_format: str | None = None,
) -> RichTermDirective:
    settings = OptionParser(components=(Parser,)).get_default_values()
    document = new_document("<test>", settings=settings)
    if with_env:
        env = SimpleNamespace(
            config=SimpleNamespace(
                richterm_prompt=config_prompt,
                richterm_hide_command=config_hide,
                richterm_shown_command=config_shown,
            )
        )
        if builder_format is not None:

            class DummyTags:
                def eval_condition(self, expr: str) -> bool:
                    if expr.strip() == "html":
                        return builder_format == "html"
                    return False

            env.app = SimpleNamespace(builder=SimpleNamespace(format=builder_format, tags=DummyTags()))
        document.settings.env = env
    state = DummyState(document)
    state_machine = DummyStateMachine(document)

    options: dict[str, object] = {}
    if prompt is not None:
        options["prompt"] = RichTermDirective.option_spec["prompt"](prompt)
    if hide_option:
        options["hide-command"] = RichTermDirective.option_spec["hide-command"](None)
    if shown_command is not None:
        options["shown-command"] = RichTermDirective.option_spec["shown-command"](shown_command)

    return RichTermDirective(
        name="richterm",
        arguments=[command],
        options=options,
        content=[],
        lineno=1,
        content_offset=0,
        block_text=command,
        state=state,
        state_machine=state_machine,
    )


def test_setup_registers_extension(mocker) -> None:
    app = mocker.Mock()
    config = setup(app)
    app.add_config_value.assert_any_call("richterm_prompt", "$", "env")
    app.add_config_value.assert_any_call("richterm_hide_command", False, "env")
    app.add_config_value.assert_any_call("richterm_shown_command", None, "env")
    app.add_directive.assert_called_with("richterm", RichTermDirective)
    assert config["version"] == get_version()


def test_directive_renders_svg() -> None:
    directive = make_directive("python -c \"print('hi')\"", prompt="[bold cyan]$")
    nodes = directive.run()
    assert len(nodes) == 1
    svg_text = _normalize_svg(nodes[0].astext())
    assert "<svg" in svg_text
    assert "hi" in svg_text
    assert "python" in svg_text


def test_directive_hide_command_option() -> None:
    directive = make_directive("python -c \"print('hi')\"", hide_option=True)
    nodes = directive.run()
    assert len(nodes) == 1
    svg_text = _normalize_svg(nodes[0].astext())
    assert "python -c" not in svg_text
    assert "hi" in svg_text


def test_directive_hide_command_from_config() -> None:
    directive = make_directive(
        "python -c \"print('hi')\"",
        config_hide=True,
        config_prompt="[bold]$",
    )
    nodes = directive.run()
    assert len(nodes) == 1
    svg_text = _normalize_svg(nodes[0].astext())
    assert "python -c" not in svg_text
    assert "hi" in svg_text


def test_directive_shown_command_option() -> None:
    directive = make_directive(
        "python -c \"print('hi')\"",
        shown_command="echo pretend",
    )
    nodes = directive.run()
    assert len(nodes) == 1
    svg_text = _normalize_svg(nodes[0].astext())
    assert "echo pretend" in svg_text
    assert "python -c" not in svg_text
    assert "hi" in svg_text


def test_directive_shown_command_from_config() -> None:
    directive = make_directive(
        "python -c \"print('hi')\"",
        config_shown="echo pretend",
    )
    nodes = directive.run()
    assert len(nodes) == 1
    svg_text = _normalize_svg(nodes[0].astext())
    assert "echo pretend" in svg_text
    assert "python -c" not in svg_text
    assert "hi" in svg_text


def test_directive_shown_command_ignored_when_hidden(mocker) -> None:
    mock_warning = mocker.patch("richterm.sphinxext.logger.warning")
    directive = make_directive(
        "python -c \"print('hi')\"",
        shown_command="echo pretend",
        hide_option=True,
    )
    nodes = directive.run()
    assert len(nodes) == 1
    svg_text = _normalize_svg(nodes[0].astext())
    assert "echo pretend" not in svg_text
    assert "python -c" not in svg_text
    assert "hi" in svg_text
    mock_warning.assert_called_once()


def test_directive_failure_raises_sphinx_error() -> None:
    directive = make_directive('python -c "import sys; sys.exit(2)"')
    with pytest.raises(SphinxError):
        directive.run()


def test_directive_html_builder_omits_fallback() -> None:
    directive = make_directive("python -c \"print('html')\"", builder_format="html")
    nodes = directive.run()
    assert len(nodes) == 1
    assert "<svg" in nodes[0].astext()


def test_directive_defaults_without_env() -> None:
    directive = make_directive("python -c \"print('ok')\"", with_env=False)
    config = directive._get_config()
    assert config.richterm_prompt == "$"
    assert config.richterm_hide_command is False
    assert config.richterm_shown_command is None


def test_directive_requires_command() -> None:
    directive = make_directive("   ")
    with pytest.raises(DirectiveError):
        directive.run()


def test_directive_invalid_command_syntax() -> None:
    directive = make_directive('python -c "unterminated')
    with pytest.raises(DirectiveError):
        directive.run()


def test_directive_command_execution_error(mocker) -> None:
    directive = make_directive("python -c \"print('x')\"")
    mocker.patch("richterm.sphinxext.run_command", side_effect=CommandExecutionError("oops"))
    with pytest.raises(DirectiveError):
        directive.run()
