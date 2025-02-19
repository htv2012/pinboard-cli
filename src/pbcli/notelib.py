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

from . import con

TITLE = "title"
ID = "id"
LENGTH = "length"
TEXT = "text"


def show(note: dict, format: str):
    if format == "full":
        con.title(note[TITLE])
        con.meta(f"ID: {note[ID]}", style="meta")
        con.meta(f"Length: {note[LENGTH]}", style="meta")
        if text := note.get(TEXT):
            con.print("---")
            con.content(text, style="content")
    elif format == "content":
        if text := note.get(TEXT):
            con.content(text, style="content")
    elif format == "json":
        con.print_json(note)
    con.print()
