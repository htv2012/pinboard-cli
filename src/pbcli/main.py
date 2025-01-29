#!/usr/bin/env python3
"""
A CLI interface into pinboard
"""

import argparse
import json
import textwrap

import click

from . import pinboard
from .config import get_auth_token


@click.group()
def main():
    pass


def parse_command_line():
    """
    Parses and packages command line arguments

    :return: An argparse.Namespace object
    """
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest="action")
    sub_parsers.required = True

    sub_parsers.add_parser("export")

    argument_parser = sub_parsers.add_parser("ls")
    argument_parser.add_argument(
        "-d",
        "--description",
    )
    argument_parser.add_argument(
        "-t",
        "--tag",
    )
    argument_parser.add_argument("-u", "--url")

    argument_parser = sub_parsers.add_parser("new")
    argument_parser.add_argument(
        "-t", "--tags", help="Multiple tags must be quoted and space separated"
    )
    argument_parser.add_argument(
        "-s", "--shared", default="no", action="store_const", const="yes"
    )
    argument_parser.add_argument(
        "-r", "--toread", default="no", action="store_const", const="yes"
    )
    argument_parser.add_argument("url")
    argument_parser.add_argument("description")

    argument_parser = sub_parsers.add_parser("rm")
    argument_parser.add_argument("urls", nargs="+")

    argument_parser = sub_parsers.add_parser("tags")

    argument_parser = sub_parsers.add_parser("rmtag")
    argument_parser.add_argument("tag")

    argument_parser = sub_parsers.add_parser("mvtag")
    argument_parser.add_argument("old_name")
    argument_parser.add_argument("new_name")

    argument_parser = sub_parsers.add_parser("notes")
    argument_parser.add_argument("-i", "--id", default=None, required=False)

    options = parser.parse_args()
    return options


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
    posts = pinboard.Posts(api, fetch=False)

    posts.refresh()
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
    posts = pinboard.Posts(api, fetch=False)

    posts.refresh()
    for url in urls:
        try:
            posts.delete(url)
        except ValueError:
            print(f"{url} not found")


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
    print(f"{url=}")
    print(f"{title=}")
    print(f"{description=}")
    print(f"{tags=}")
    print(f"{force_overwrite=}")
    print(f"{public=}")
    print(f"{reading_list=}")


    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)
    posts = pinboard.Posts(api, fetch=False)

    posts.create(
        url=url,
        title=title,
        description=description,
        tags=tags,
        force_overwrite=force_overwrite,
        public=public,
        reading_list=reading_list,
    )


@main.command()
def tags():
    """Lists the tags, sorted by tag name"""
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)
    tags = api.get_tags()
    tags_cloud = " ".join("%s(%d)" % item for item in tags.items())
    print(textwrap.fill(tags_cloud))


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


# def main():
#    """
#    Entry
#    """
#    auth_token = get_auth_token()
#    api = pinboard.Pinboard(auth_token)
#    posts = pinboard.Posts(api, fetch=False)
#    options = parse_command_line()
#
#    if options.action == "ls":
#        list_posts(posts, options.description, options.tag, options.url)
#    elif options.action == "new":
#        create_post(
#            posts,
#            url=options.url,
#            description=options.description,
#            tags=options.tags,
#            shared=options.shared,
#            toread=options.toread,
#        )
#    elif options.action == "rm":
#        remove_posts(posts, options.urls)
#    elif options.action == "export":
#        export_posts(api)
#    elif options.action == "tags":
#        list_tags(api)
#    elif options.action == "rmtag":
#        api.tag_delete(options.tag)
#    elif options.action == "mvtag":
#        api.tag_rename(options.old_name, options.new_name)
#    elif options.action == "notes":
#        list_notes(api, options.id)
