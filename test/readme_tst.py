#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 07:41:19 2017

@author: pietro
"""
from grass_session import Session
from grass.script import core as gcore


GRASS_COMPRESSOR="ZSTD"
GRASS_ZLIB_LEVEL=6
GRASS_COMPRESS_NULLS=1

print("creating location")
with Session(gisdb="/tmp", location="location",
             create_opts="EPSG:4326"):
    print("Inside grass session")
    print(gcore.parse_command("g.gisenv", flags="s"))
print("location created!")

print("creating mapset")
with Session(gisdb="/tmp", location="location", mapset="test",
             create_opts=""):
    print(gcore.parse_command("g.gisenv", flags="s"))
print("mapset created!")
print("done!")
