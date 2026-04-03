# Configuration (Reference)

This chapter is a lookup reference for environment variables that affect `richterm` behavior directly.

```{glossary}
RICHTERM_DISABLE_COLOR_HINT
  Disables the extra color-friendly environment hints that `richterm` normally injects before running a command.
  When set to `1`, `richterm` leaves the child environment unchanged.

NO_COLOR
  Standard opt-out flag for colored terminal output.
  `richterm` respects this convention through the underlying Rich rendering behavior unless color is explicitly forced.
  Reference: <https://no-color.org/>

FORCE_COLOR
  Forces color output in environments that would otherwise disable it.
  `richterm` uses it as one of the hints for non-interactive command captures.

TERM
  Terminal capability identifier passed to the executed command.
  If `TERM` is missing or set to `dumb`, `richterm` defaults it to `xterm-256color` to improve captured styling.
```
