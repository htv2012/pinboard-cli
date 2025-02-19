"""Console output"""

import functools

import rich.console
import rich.json
import rich.theme

THEME = rich.theme.Theme(
    {
        "title": "light_goldenrod1",
        "meta": "bright_black",
        "content": "white",
        "error": "red",
    }
)


_console = rich.console.Console(theme=THEME)
print = _console.print
out = _console.print
title = functools.partial(_console.print, style="title")
meta = functools.partial(_console.print, style="meta")
content = functools.partial(_console.print, style="content")
error = functools.partial(_console.print, style="error")
