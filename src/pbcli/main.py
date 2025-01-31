#!/usr/bin/env python3
"""
A CLI interface into pinboard
"""

import json
import operator
import textwrap

import click

from . import columnize, pinboard
from .config import get_auth_token


@click.group()
@click.version_option()
def main():
    pass


@main.command()
@click.option("-d", "--description")
@click.option("-t", "--tag")
@click.option("-u", "--url")
def ls(description, tag, url):
    """
    Lists posts. If description, tag, or url are supplied, then perform
    a wildcard search by those fields
    """
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)

    posts = api.get_posts()
    posts = filter(lambda p: p.match(description, tag, url), posts)
    posts = sorted(posts, key=lambda p: p.description.lower())
    for post in posts:
        description = textwrap.fill(
            post.description,
            width=72,
            subsequent_indent="             ",
        )
        print(f"Description: {description}")
        if post.extended:
            extended = textwrap.fill(
                f"{post.extended}",
                width=72,
                initial_indent="             ",
                subsequent_indent="             ",
            )
            print(f"{extended}")
        print(f"URL:         {post.href}")
        if post.tags:
            print(f"Tags:        {post.tags}")
        print()


@main.command()
@click.argument("urls", nargs=-1)
def rm(urls):
    """Removes a list of URLs"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)
    for url in urls:
        result = api.delete_post(url)
        if (code := result["result_code"]) != "done":
            # TODO: output in error color
            print(f"{url}: {code}")


@main.command()
def export():
    """Exports all posts to JSON"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)

    json_posts = api.get_posts()
    print(json.dumps(json_posts, sort_keys=True, indent=4))


@main.command()
@click.argument("url")
@click.argument("title")
@click.option("-d", "--description")
@click.option("-t", "--tags", multiple=True)
@click.option("-f", "--force-overwrite", is_flag=True, default=False)
@click.option("-p", "--public", is_flag=True, default=False)
@click.option("-r", "--reading-list", is_flag=True, default=False)
def add(
    url,
    title,
    description,
    tags,
    force_overwrite,
    public,
    reading_list,
):
    """Creates a new post"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)

    result = api.add_post(
        url=url,
        title=title,
        description=description,
        tags=tags,
        force_overwrite=force_overwrite,
        public=public,
        reading_list=reading_list,
    )
    if result["result_code"] != "done":
        # TODO: use color
        print(result["result_code"])


@main.command()
@click.option("-s", "--sort-by", type=click.Choice(["name", "count"]), default="name")
def tags(sort_by):
    """Lists the tags, sorted by tag name"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)

    if sort_by == "name":
        key = operator.itemgetter(0)
        reverse = False
    else:
        key = operator.itemgetter(1)
        reverse = True

    tags = api.get_tags()
    tags = [
        f"{name}({count})"
        for name, count in sorted(tags.items(), key=key, reverse=reverse)
    ]
    columnize.columnize(tags)


@main.command()
@click.argument("note_id", required=False)
def notes(note_id):
    """List note titles, or display individual note"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)

    notes = api.notes
    if note_id is None:
        for note in notes:
            print(f"{note}")
    else:
        found = next((note for note in notes if note.id == note_id), None)
        if found is None:
            raise SystemExit(f"ID not found: {note_id}")
        print(found.title)
        print()
        print(found.text)
