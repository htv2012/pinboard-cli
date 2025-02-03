#!/usr/bin/env python3
"""
A CLI interface into pinboard
"""

import json
import operator

import click

from . import bookmarklib, columnize, notelib, pinboard
from .config import get_auth_token


def get_api():
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)
    return api


@click.group()
@click.pass_context
@click.version_option()
def main(ctx):
    auth_token = get_auth_token()

    ctx.ensure_object(dict)
    ctx.obj["api"] = pinboard.Pinboard(auth_token)


@main.command()
@click.pass_context
@click.option("-t", "--tags", multiple=True, help="Up to 3 tags")
@click.option("-c", "--count", type=click.IntRange(1, 100))
def recent(ctx, tags, count):
    """Lists recent bookmarks and notes"""
    if len(tags) > 3:
        ctx.fail("Number of tags should not exceed 3")
    result = ctx.obj["api"].get_recent_posts(tags=tags, count=count)

    for entry in result["posts"]:
        bookmarklib.show(entry)


@main.command()
def stat():
    """Shows some stastistics"""
    api = get_api()

    bookmarks = api.get_all_posts()
    print(f"Bookmarks count: {len(bookmarks)}")

    notes = api.get_all_notes()
    print(f"Notes count: {len(notes)}")

    tags = api.get_tags()
    print(f"Tags count: {len(tags)}")

    result = api.get_last_update()
    print(f"Last Update: {result['update_time']}")


@main.command()
@click.option("-n", "--name", type=str.casefold, metavar="TEXT")
@click.option("-d", "--description", type=str.casefold, metavar="TEXT")
@click.option("-t", "--tag", multiple=True, type=str.casefold, metavar="TEXT")
@click.option("-u", "--url")
def ls(name, description, tag, url):
    """Lists all posts"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)

    posts = api.get_all_posts()
    posts = filter(bookmarklib.by_name(name), posts)
    posts = filter(bookmarklib.by_description(description), posts)
    posts = filter(bookmarklib.by_tag(tag), posts)
    posts = filter(bookmarklib.by_url(url), posts)

    for post in posts:
        bookmarklib.show(post)


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

    json_posts = api.get_all_posts()
    print(json.dumps(json_posts, indent=4))


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
@click.option(
    "-f", "--format", type=click.Choice(["full", "content", "json"]), default="full"
)
def notes(format):
    """List note titles, or display individual note"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)
    result = api.get_all_notes()

    if format == "json":
        notelib.show_json(result)
    else:
        for entry in result["notes"]:
            notelib.show(entry, format)


@main.command()
@click.pass_context
@click.option(
    "-f", "--format", type=click.Choice(["full", "content", "json"]), default="full"
)
@click.argument("note_id")
def note(ctx, note_id, format):
    """Shows a single note"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)

    if entry := api.get_note(note_id):
        notelib.show(entry, format)
    else:
        notelib.show_not_found(note_id)
        ctx.exit(1)
