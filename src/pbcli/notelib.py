"""
Notes support

A sample note, which the API return:

{
      "0": "b7247b606fcb7f20b562",
      "1": "64b7a23f090a39abcd22",
      "2": "First Task",
      "3": 157,
      "4": "2021-09-06 18:37:03",
      "5": "2025-01-31 20:26:07",
      "id": "b7247b606fcb7f20b562",
      "hash": "64b7a23f090a39abcd22",
      "title": "First Task",
      "length": 157,
      "created_at": "2021-09-06 18:37:03",
      "updated_at": "2025-01-31 20:26:07"
    }
"""

import rich.console
import rich.json
import rich.theme

TITLE = "title"
ID = "id"
LENGTH = "length"
TEXT = "text"

NOTE_THEME = rich.theme.Theme(
    {
        "title": "light_goldenrod1",
        "meta": "bright_black",
        "content": "white",
        "error": "red",
    }
)


def show(note: dict, format: str):
    console = rich.console.Console(theme=NOTE_THEME)
    if format == "full":
        console.print(note[TITLE], style="title")
        console.print(f"ID: {note[ID]}", style="meta")
        console.print(f"Length: {note[LENGTH]}", style="meta")
        if text := note.get(TEXT):
            console.print("---")
            console.print(text, style="content")
    elif format == "content":
        if text := note.get(TEXT):
            console.print(text, style="content")
    elif format == "json":
        show_json(note)
    console.print()


def show_not_found(note_id: str):
    console = rich.console.Console(theme=NOTE_THEME)
    console.print(f"Note ID not found: {note_id}", style="error")


def show_json(data: dict):
    console = rich.console.Console(theme=NOTE_THEME)
    console.print(rich.json.JSON.from_data(data, indent=2))
