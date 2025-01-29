#!/usr/bin/env python3
"""
A CLI interface into pinboard
"""

import argparse
import json
import textwrap


from . import pinboard
from .config import get_auth_token


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


def list_posts(posts, description=None, tag=None, url=None):
    """
    Lists posts. If description, tag, or url are supplied, then perform
    a wildcard search by those fields

    :param description: A search string which might contains wildcard
    :param tag: A search string which might contains wildcard
    :param url: A search string which might contains wildcard
    """
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


def remove_posts(posts, urls):
    """
    Removes a list of URLs

    :param posts: An object of type pinboard.Post
    :param urls: A list of URLs to remove
    """
    posts.refresh()
    for url in urls:
        try:
            posts.delete(url)
        except ValueError:
            print(f"{url} not found")


def export_posts(api):
    """
    Exports all posts to JSON

    :param api: A PinboardApi object
    """
    json_posts = api.get_posts()
    print(json.dumps(json_posts, sort_keys=True, indent=4))


def create_post(
    posts,
    url,
    description,
    extended=None,
    tags=None,
    replace="yes",
    shared="no",
    toread="no",
):
    """
    Creates a new post

    :param posts: A pinboard.Posts object
    :param url: A string representing the URL
    :param description: The first line of the description (title)
    :param extended: The subsequent line of the description
    :param tags: A space-separated string representing the tags
    :param replace: A yes/no indicate to replace existing entries if needed
    :param shared: A yes/no to indicate public post
    :param toread: A yes/no to place the post into a read list
    """
    posts.create(
        url=url,
        description=description,
        extended=extended,
        tags=tags,
        replace=replace,
        shared=shared,
        toread=toread,
    )


def list_tags(api):
    """
    Lists the tags, sorted by tag name

    :param api: A PinboardApi object
    """
    tags = api.get_tags()
    tags_cloud = " ".join("%s(%d)" % item for item in tags.items())
    print(textwrap.fill(tags_cloud))


def list_notes(api, note_id=None):
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


def main():
    """
    Entry
    """
    auth_token = get_auth_token()
    api = pinboard.Pinboard(auth_token)
    posts = pinboard.Posts(api, fetch=False)
    options = parse_command_line()

    if options.action == "ls":
        list_posts(posts, options.description, options.tag, options.url)
    elif options.action == "new":
        create_post(
            posts,
            url=options.url,
            description=options.description,
            tags=options.tags,
            shared=options.shared,
            toread=options.toread,
        )
    elif options.action == "rm":
        remove_posts(posts, options.urls)
    elif options.action == "export":
        export_posts(api)
    elif options.action == "tags":
        list_tags(api)
    elif options.action == "rmtag":
        api.tag_delete(options.tag)
    elif options.action == "mvtag":
        api.tag_rename(options.old_name, options.new_name)
    elif options.action == "notes":
        list_notes(api, options.id)


if __name__ == "__main__":
    main()
