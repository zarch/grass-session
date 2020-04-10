#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:49:43 2020

@author: pietro
"""
import sys

import pytest
from grass_session import get_platform_name


def test__get_platform_name(monkeypatch):
    """Return an identification string with the platform name, raise
    an exception if the platform is unknown/unsupported.

    if sys.platform == "win32":
        return "win32"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform.startswith("sunos"):
        return "solaris"
    elif sys.platform.startswith("hp-ux"):
        return "hp-ux"
    elif sys.platform.startswith("aix"):
        return "aix"
    elif sys.platform == "darwin":
        return "darwin"
    elif sys.platform.startswith("freebsd"):
        return "freebsd"
    elif sys.platform.startswith("openbsd"):
        return "openbsd"
    elif sys.platform.startswith("netbsd"):
        return "netbsd"
    else:
        raise RuntimeError("unknown platform: '%s'" % sys.platform)
    """
    supported_platforms = [
        "win32",
        "linux-unknown",
        "sunos-unknown",
        "hp-ux-unknown",
        "aix-unknown",
        "darwin",
        "freebsd-unknown",
        "openbsd-unknown",
        "netbsd-unknown",
    ]
    results = [
        "win32",
        "linux",
        "solaris",
        "hp-ux",
        "aix",
        "darwin",
        "freebsd",
        "openbsd",
        "netbsd",
    ]
    for plat, res in zip(supported_platforms, results):
        monkeypatch.setattr(sys, "platform", plat)
        assert get_platform_name() == res

    monkeypatch.setattr(sys, "platform", "redox")
    with pytest.raises(RuntimeError):
        get_platform_name()
