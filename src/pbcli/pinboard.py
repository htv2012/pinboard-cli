#!/usr/bin/env python
"""
This module provides the tools to interact with https://pinboard.in
service
"""

import collections.abc
import html
import json
import logging
import os
import ssl
import urllib.parse
import urllib.request

logging.basicConfig(level=os.getenv("LOGLEVEL", "WARN"))
LOGGER = logging.getLogger(__name__)


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
        params = {k: v for k, v in list(kwargs.items()) if v is not None}
        url = self._build_url(method, **params)
        LOGGER.debug("call_api with url=%s", url)
        context = ssl.SSLContext()
        response = urllib.request.urlopen(url, context=context)
        result = response.read()
        result = json.loads(result)
        return result

    def get_tags(self):
        """
        Gets a list of tags

        :return: a dictionary of {tag: count}
        """
        result = self.call_api("tags/get")
        result = {html.unescape(k): int(v) for k, v in sorted(result.items())}
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

    def get_posts(self):
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
        url,
        description,
        extended=None,
        tags=None,
        replace="yes",
        shared="no",
        toread="no",
    ):
        """
        Create a new post or update an existing URL

        :param url: The URL to add
        :param description: Really the title
        :param extended: The real description
        :param tags: A list of tags, separated by spaces
        :param replace: "yes" or "no". If yes, replace the existing
            URL. If no, create a new post despite the duplicate URLs
        :param shared: "yes" means public, "no" means private
        :param toread: "yes" means to put into the to-read list, "no"
            means do not put in the list
        :return: a dictionary
        """
        args = dict(
            url=url,
            description=description,
            extended=extended,
            tags=tags,
            replace=replace,
            shared=shared,
            toread=toread,
        )
        args = {k: v for k, v in args.items() if v is not None}
        result = self.call_api("posts/add", **args)
        return result

    @property
    def notes(self):
        result = self.call_api("notes/list")
        notes = [Note(raw, self) for raw in result["notes"]]
        return notes


class Note:
    def __init__(self, raw, api):
        self._raw = raw
        self._api = api
        self.id = raw["id"]
        self.title = raw["title"]

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
            f"https://pinboard.in/u:htv2017/notes/{self.id}",
        )


class Post:
    """
    A single post (bookmark)
    """

    def __init__(self, post_as_dict):
        self.description = post_as_dict["description"]
        self.extended = post_as_dict["extended"]
        self.hash_value = post_as_dict["hash"]
        self.href = post_as_dict["href"]
        self.meta = post_as_dict["meta"]
        self.shared = post_as_dict["shared"]
        self.tags = post_as_dict["tags"]
        self.time_stamp = post_as_dict["time"]
        self.toread = post_as_dict["toread"]

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


class Posts(collections.abc.MutableSequence):
    """
    A collection of posts
    """

    def __init__(self, api, fetch=True):
        self.api = api
        self.posts = None
        if fetch:
            self.refresh()

    def __getitem__(self, key):
        return self.posts[key]

    def __setitem__(self, key, value):
        print(f"__setitem__ key={key}, value={value}")
        self.posts[key] = value

    def __delitem__(self, key):
        raise NotImplementedError("No need for this method in this context")

    def insert(self, index, value):
        raise NotImplementedError("No need for this method in this context")

    def __len__(self):
        return len(self.posts)

    def refresh(self):
        """
        Retrieves posts from the server
        """
        self.posts = [Post(fields) for fields in self.api.get_posts()]

    def create(
        self,
        url,
        description,
        extended=None,
        tags=None,
        replace="yes",
        shared="no",
        toread="no",
    ):
        """
        Creates a post (bookmark)
        """

        result = self.api.add_post(
            url, description, extended, tags, replace, shared, toread
        )
        LOGGER.debug("Add post, result = %r", result)

    def delete(self, url):
        """
        Deletes a post by url

        :param url: A string representing the URL to delete
        """
        LOGGER.debug("Deleting URL: %r", url)
        result = self.api.delete_post(url)
        LOGGER.debug("Result: %r", result)
        if result["result_code"] == "item not found":
            raise ValueError("list.remove(x): x not in list")

        # Update the underline posts
        self.posts = [post for post in self.posts if post.href != url]


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
