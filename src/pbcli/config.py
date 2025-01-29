#!/usr/bin/env python3
"""
config.py
Configuration management
"""

import os
import pathlib
import platform

import tomllib



def get_auth_token():
    """
    Retrieve the API token from the configuration file

    :return: The auth token
    """
    system = platform.system()
    if system in {"Darwin", "Linux", "FreeBSD"}:
        config_filename = pathlib.Path("~/.config/pbcli.toml").expanduser()
    else:
        raise SystemExit(f"get_auth_token not implemented for {system}")

    if not os.path.exists(config_filename):
        raise SystemExit(
            "Please create" + config_filename + " with:\n"
            '{"auth token": "(add your API token here)"}'
        )

    with open(config_filename, "rb") as stream:
        config = tomllib.load(stream)

    return config["auth-token"]
