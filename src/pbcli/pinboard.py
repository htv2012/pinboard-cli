#!/usr/bin/env python
"""
This module provides the tools to interact with https://pinboard.in
service
"""

import json
import logging
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request

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
        return result

    def get_note(self, note_id: str):
        try:
            # See notes-ID.json for a sample result
            result = self.call_api(f"notes/{note_id}")
            return result
        except urllib.error.HTTPError:
            # Not found
            return None
