#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:49:43 2020

@author: pietro
"""
import os
import subprocess

from grass_session import get_grass_bin


def test__get_grass_bin(monkeypatch):
    """Return the path to the GRASS GIS binary file command.
    If available takes the value from os.environ GRASSBIN variable.
    grassbin = os.environ.get("GRASSBIN")
    if grassbin:
        return grassbin

    platform = get_platform_name()
    grassbin_pattern = DEFAULTGRASSBIN.get(platform, DEFAULTBIN)

    versions = [version] if version else ["78", "76", "74"]
    for version in versions:
        grassbin = grassbin_pattern.format(version=version)
        try:
            with open(os.devnull, "w+b") as devnull:
                subprocess.check_call(
                    [grassbin, "--config"], stdout=devnull, stderr=subprocess.STDOUT
                )
            return grassbin
        except OSError:
            pass
    """
    grassbin = "grass10k"

    # check the enviornment varible
    def get(key):
        return grassbin

    monkeypatch.setattr(os.environ, "get", get)
    assert get_grass_bin() == grassbin

    # ---
    def check_call(*args, **kwargs):
        return None

    monkeypatch.setattr(subprocess, "check_call", check_call)
    assert get_grass_bin(version="10k") == grassbin
