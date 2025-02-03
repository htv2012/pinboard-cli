#!/usr/bin/env python
"""
This module provides the tools to interact with https://pinboard.in
service
"""

import json
import logging
import os
import ssl
import urllib.parse
import urllib.request

from .config import get_user

logging.basicConfig(level=os.getenv("LOGLEVEL", "WARN"))
LOGGER = logging.getLogger(__name__)


def yes_no(value: bool):
    if value:
        return "yes"
    return "no"


class Pinboard:
    """
    An API to pinboard.in service
    """

    def __init__(self, auth_token):
        self.query = dict(auth_token=auth_token, format="json")
        self.version = "/v1/"

    def _build_url(self, method, **kwargs):
        """
        Build the URL for a given method and arguments
        """
        query = {**self.query, **kwargs}
        query_string = urllib.parse.urlencode(query)
        url = urllib.parse.urlunsplit(
            ("https", "api.pinboard.in", self.version + method, query_string, "")
        )
        return url

    def call_api(self, method, **kwargs):
        """
        Call the API for a method
        """
        params = {k: v for k, v in kwargs.items() if v is not None}
        url = self._build_url(method, **params)
        LOGGER.debug("call_api with url=%s", url)
        context = ssl.SSLContext()
        response = urllib.request.urlopen(url, context=context)
        result = response.read()
        result = json.loads(result)
        return result

    def get_last_update(self):
        result = self.call_api("posts/update")
        return result

    def get_tags(self):
        """
        Gets a list of tags

        :return: a dictionary of {tag: count}
        """
        result = self.call_api("tags/get")
        return result

    def tag_delete(self, tag_name):
        """
        Deletes a tag, but not the posts themselves

        :param tag_name: The name of the tag, case sensitive
        """
        self.call_api("tags/delete", tag=tag_name)

    def tag_rename(self, old_name, new_name):
        """
        Renames a tag

        :param old_name: A string representing the old name
        :param new_name: A string representing the new name
        """

        self.call_api("tags/rename", old=old_name, new=new_name)

    def get_recent_posts(self, tags: tuple[str] = None, count: int = None):
        """Retrieve recent posts"""
        result = self.call_api("posts/recent", tags=tags or None, count=count)
        return result

    def get_all_posts(self):
        """
        Retrieve a list of all posts

        :return: A JSON object representing a list of posts
        """
        result = self.call_api("posts/all")
        return result

    def delete_post(self, url):
        """
        Deletes a post represented by the URL

        :param url: A string representing the URL to delete
        """

        result = self.call_api("posts/delete", url=url)
        return result

    def add_post(
        self,
        url: str,
        title: str,
        description: str = None,
        tags: list[str] = None,
        force_overwrite: bool = False,
        public: bool = False,
        reading_list: bool = False,
    ):
        """Create a new post or update an existing URL"""
        kwargs = dict(
            url=url,
            description=title,
            replace=yes_no(force_overwrite),
            shared=yes_no(public),
            toread=yes_no(reading_list),
        )
        if description:
            kwargs["extended"] = description
        if tags:
            kwargs["tags"] = ",".join(tags)

        result = self.call_api("posts/add", **kwargs)
        return result

    def get_all_notes(self):
        result = self.call_api("notes/list")
        notes = [Note(raw, self) for raw in result["notes"]]
        return notes


class Note:
    def __init__(self, raw, api):
        self._raw = raw
        self._api = api
        self.id = raw["id"]
        self.title = raw["title"]
        self.user = get_user()

    @property
    def text(self):
        result = self._api.call_api(f"notes/{self.id}")
        return result["text"]

    def __repr__(self):
        return f"Note(id={self.id!r}, title={self.title!r})"

    def __str__(self):
        return "%s\n  ID: %s\n  URL: %s" % (
            self.title,
            self.id,
            f"https://pinboard.in/u:{self.user}/notes/{self.id}",
        )


class Post:
    """
    A single post (bookmark)
    """

    def __init__(self, raw):
        self.description = raw["description"]
        self.extended = raw["extended"]
        self.hash_value = raw["hash"]
        self.href = raw["href"]
        self.meta = raw["meta"]
        self.shared = raw["shared"]
        self.tags = raw["tags"]
        self.time_stamp = raw["time"]
        self.toread = raw["toread"]
        self._raw = raw

    def __repr__(self):
        return f"Post(description={self.description!r}, href={self.href!r})"

    def __eq__(self, other):
        LOGGER.debug("Compare: %s with %s", self, other)
        try:
            return self.href == other.href
        except AttributeError:
            return self.href == other

    def match(self, description=None, tag=None, url=None, ignore_case=True):
        """
        A predicate to match the this post against a list of criteria

        :param description: None for automatic match, a string for
            partial match
        :param tag: None for automatic match, a string for partial match
        :param url: None for automatic match, a string for partial match
        :param ignore_case: True (default) for case insensitive match,
            False for case sensitive match
        :return: A boolean to indicate if this post matches the criteria
        """

        return (
            _matched(description, self.description, ignore_case)
            and _matched(tag, self.tags, ignore_case)
            and _matched(url, self.href, ignore_case)
        )


def _matched(search_term, text, ignore_case):
    """
    Matches a search term against the text

    :param search_term: None for automatic match, a string for partial
        match
    :param text: The text to match against the search term
    :param ignore_case: True to ignore case, False to perform case
        sensitive match
    :return: A boolean indicate if a match was found
    """

    if search_term is None:
        return True

    if ignore_case:
        search_term = search_term.lower()
        text = text.lower()

    return search_term in text
