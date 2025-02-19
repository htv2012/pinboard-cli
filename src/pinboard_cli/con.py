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


_CONSOLE = rich.console.Console(theme=THEME)

print = _CONSOLE.print
out = _CONSOLE.print
title = functools.partial(_CONSOLE.print, style="title")
meta = functools.partial(_CONSOLE.print, style="meta")
content = functools.partial(_CONSOLE.print, style="content")
error = functools.partial(_CONSOLE.print, style="error")


def print_json(data: dict):
    _CONSOLE.print(rich.json.JSON.from_data(data, indent=2))
