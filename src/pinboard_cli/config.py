#!/usr/bin/env python3
"""
config.py
Configuration management
"""

import os
import pathlib
import platform

import tomllib


def get_config():
    """
    Retrieve the contents of the configuration file
    """
    system = platform.system()
    if system in {"Darwin", "Linux", "FreeBSD"}:
        config_filename = pathlib.Path("~/.config/pinboard-cli.toml").expanduser()
    else:
        raise SystemExit(f"get_auth_token not implemented for {system}")

    if not os.path.exists(config_filename):
        with open(config_filename, "w") as stream:
            stream.write('auth-token = "Add your auth token here"\n')
            stream.write('user = "Add your user name here"\n')
        raise SystemExit(
            f"Please edit {config_filename} and add the the required configurations."
        )

    with open(config_filename, "rb") as stream:
        config = tomllib.load(stream)

    return config


def get_auth_token():
    config = get_config()
    return config["auth-token"]


def get_user():
    config = get_config()
    return config["user"]
