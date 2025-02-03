#!/usr/bin/env python3
"""
A CLI interface into pinboard
"""

import json
import operator

import click

from . import bookmarklib, columnize, notelib, pinboard
from .config import get_auth_token


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
@click.pass_context
def stat(ctx):
    """Shows some stastistics"""
    bookmarks = ctx.obj["api"].get_all_posts()
    print(f"Bookmarks count: {len(bookmarks)}")

    notes = ctx.obj["api"].get_all_notes()
    print(f"Notes count: {len(notes)}")

    tags = ctx.obj["api"].get_tags()
    print(f"Tags count: {len(tags)}")

    result = ctx.obj["api"].get_last_update()
    print(f"Last Update: {result['update_time']}")


@main.command()
@click.pass_context
@click.option("-n", "--name", type=str.casefold, metavar="TEXT")
@click.option("-d", "--description", type=str.casefold, metavar="TEXT")
@click.option("-t", "--tag", multiple=True, type=str.casefold, metavar="TEXT")
@click.option("-u", "--url")
def ls(ctx, name, description, tag, url):
    """Lists all posts"""
    posts = ctx.obj["api"].get_all_posts()
    posts = filter(bookmarklib.by_name(name), posts)
    posts = filter(bookmarklib.by_description(description), posts)
    posts = filter(bookmarklib.by_tag(tag), posts)
    posts = filter(bookmarklib.by_url(url), posts)

    for post in posts:
        bookmarklib.show(post)


# TODO: error if no url specified
@main.command()
@click.pass_context
@click.argument("urls", nargs=-1)
def rm(ctx, urls):
    """Removes a list of URLs"""
    for url in urls:
        result = ctx.obj["api"].delete_post(url)
        if (code := result["result_code"]) != "done":
            # TODO: output in error color
            print(f"{url}: {code}")


@main.command()
@click.pass_context
def export(ctx):
    """Exports all posts to JSON"""
    json_posts = ctx.obj['api'].get_all_posts()
    print(json.dumps(json_posts, indent=4))


@main.command()
@click.pass_context
@click.argument("url")
@click.argument("title")
@click.option("-d", "--description")
@click.option("-t", "--tags", multiple=True)
@click.option("-f", "--force-overwrite", is_flag=True, default=False)
@click.option("-p", "--public", is_flag=True, default=False)
@click.option("-r", "--reading-list", is_flag=True, default=False)
def add(
    ctx,
    url,
    title,
    description,
    tags,
    force_overwrite,
    public,
    reading_list,
):
    """Creates a new post"""
    result = ctx.obj["api"].add_post(
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
@click.pass_context
@click.option("-s", "--sort-by", type=click.Choice(["name", "count"]), default="name")
def tags(ctx, sort_by):
    """Lists the tags, sorted by tag name"""
    if sort_by == "name":
        key = operator.itemgetter(0)
        reverse = False
    else:
        key = operator.itemgetter(1)
        reverse = True

    tags = ctx.obj["api"].get_tags()
    tags = [
        f"{name}({count})"
        for name, count in sorted(tags.items(), key=key, reverse=reverse)
    ]
    columnize.columnize(tags)


@main.command()
@click.pass_context
@click.option(
    "-f", "--format", type=click.Choice(["full", "content", "json"]), default="full"
)
def notes(ctx, format):
    """List note titles, or display individual note"""
    result = ctx.obj["api"].get_all_notes()

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
    if entry := ctx.obj["api"].get_note(note_id):
        notelib.show(entry, format)
    else:
        notelib.show_not_found(note_id)
        ctx.exit(1)
