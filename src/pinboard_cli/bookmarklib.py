import functools
from typing import Optional

import rich.console

NAME = "description"
DESCRIPTION = "extended"
TAGS = "tags"
URL = "href"


def show(bookmark: dict):
    console = rich.console.Console()
    console.print(bookmark["description"], style="light_goldenrod1")
    if description := bookmark.get("extended"):
        console.print(description)
    if tags := bookmark.get("tags"):
        console.print(f"Tags: {tags}")
    console.print(bookmark["href"])
    console.print()


def by_key(key: str, value: Optional[str] = None):
    def match(bookmark) -> bool:
        return value is None or value.casefold() in bookmark[key].casefold()

    return match


def by_tag(target: tuple[str]):
    def match(bookmark) -> bool:
        tags = set(bookmark[TAGS].casefold().split())
        return tags.issuperset(target)

    return match


by_name = functools.partial(by_key, NAME)
by_description = functools.partial(by_key, DESCRIPTION)
by_url = functools.partial(by_key, URL)
