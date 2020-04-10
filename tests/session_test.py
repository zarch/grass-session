# -*- coding: utf-8 -*-
import os
import shutil
import sys
import tempfile

import pytest
from grass_session import Session, get_grass_bin, grass_create


"""
from grass_session import Session
from grass.script import core as gcore


GRASS_COMPRESSOR="ZSTD"
GRASS_ZLIB_LEVEL=6
GRASS_COMPRESS_NULLS=1


print("creating location")
with Session(gisdb="/tmp", location="location",
             create_opts="EPSG:4326"):
    print(gcore.parse_command("g.gisenv", flags="s"))
print("location created!")

print("creating mapset")
with Session(gisdb="/tmp", location="location", mapset="test",
             create_opts=""):
    print(gcore.parse_command("g.gisenv", flags="s"))
print("mapset created!")
print("done!")
"""


@pytest.fixture(scope="function")
def tmp_vars(request):
    tmpdir = tempfile.mkdtemp()
    location_name = "location"
    location_path = os.path.join(tmpdir, location_name)
    mapset_name = "test"
    mapset_path = os.path.join(location_path, mapset_name)

    def finalizer():
        print("teardown")
        shutil.rmtree(location_path, ignore_errors=False)

    print("setup")
    request.addfinalizer(finalizer)
    return dict(
        tmpdir=tmpdir,
        location_name=location_name,
        location_path=os.path.join(tmpdir, location_name),
        create_opts="EPSG:3035",
        mapset_name=mapset_name,
        mapset_path=mapset_path,
        grassbin=get_grass_bin(),
    )


def __check_PERMANENT_in_folder(location_path):
    assert "PERMANENT" in os.listdir(location_path)


def __check_mandatory_files(mapset_path, files):
    assert os.path.exists(mapset_path) is True
    genfiles = set(os.listdir(mapset_path))
    # check that all the generated files are the one required by GRASS GIS
    for fl in files:
        assert fl in genfiles


def __check_mandatory_files_in_PERMANENT(mapset_path):
    files = [
        "DEFAULT_WIND",
        "MYNAME",
        "PROJ_EPSG",
        "PROJ_INFO",
        "PROJ_UNITS",
        "sqlite",
        "VAR",
        "WIND",
    ]
    __check_mandatory_files(mapset_path, files)


def __check_mandatory_files_in_mapset(mapset_path):
    files = ["sqlite", "VAR", "WIND"]
    __check_mandatory_files(mapset_path, files)


def __check_epsg(mapset_path, epsg_code):
    with open(os.path.join(mapset_path, "PROJ_EPSG"), mode="r") as prj:
        assert prj.readlines() == ["epsg: {epsg_code}\n".format(epsg_code=epsg_code)]


def __grass_create(grassbin, location_path, create_opts, mapset_path):
    grass_create(grassbin=grassbin, path=location_path, create_opts=create_opts)
    # check if PERMANENT has been created
    __check_PERMANENT_in_folder(location_path)

    # check files
    permanent = os.path.join(location_path, "PERMANENT")
    __check_mandatory_files_in_PERMANENT(permanent)

    # check PROJ_EPSG content
    __check_epsg(permanent, 3035)

    # check creation of a mapset
    grass_create(grassbin=grassbin, path=mapset_path, create_opts="")
    __check_mandatory_files_in_mapset(mapset_path)


def test__grass_create(tmp_vars):
    __grass_create(
        grassbin=tmp_vars["grassbin"],
        location_path=tmp_vars["location_path"],
        create_opts=tmp_vars["create_opts"],
        mapset_path=tmp_vars["mapset_path"],
    )


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test__grass_create__with_pathlib(tmp_vars):
    import pathlib

    __grass_create(
        grassbin=pathlib.Path(tmp_vars["grassbin"]),
        location_path=pathlib.Path(tmp_vars["location_path"]),
        create_opts=tmp_vars["create_opts"],
        mapset_path=pathlib.Path(tmp_vars["mapset_path"]),
    )


def __Session_create(tmp_vars):

    from grass.pygrass.modules.shortcuts import general as g

    with Session(
        gisdb=tmp_vars["tmpdir"],
        location=tmp_vars["location_name"],
        create_opts=tmp_vars["create_opts"],
    ):
        # execute some command inside PERMANENT
        g.mapsets(flags="l")
        g.list(type="raster", flags="m")

    # check if PERMANENT has been created
    __check_PERMANENT_in_folder(tmp_vars["location_path"])

    # check files
    permanent = os.path.join(tmp_vars["location_path"], "PERMANENT")
    __check_mandatory_files_in_PERMANENT(permanent)

    # check PROJ_EPSG content
    __check_epsg(permanent, 3035)

    # check creation of a mapset
    with Session(
        gisdb=tmp_vars["tmpdir"],
        location=tmp_vars["location_name"],
        mapset=tmp_vars["mapset_name"],
        create_opts="",
    ):
        # execute some command inside user
        g.mapsets(flags="l")
        g.list(type="raster", flags="m")

    __check_mandatory_files_in_mapset(tmp_vars["mapset_path"])


def test__Session__create(tmp_vars):
    __Session_create(tmp_vars)


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test__Session__create__with_pathlib(tmp_vars):
    import pathlib

    tmp_vars.update(
        dict(
            grassbin=pathlib.Path(tmp_vars["grassbin"]),
            location_path=pathlib.Path(tmp_vars["location_path"]),
            mapset_path=pathlib.Path(tmp_vars["mapset_path"]),
        )
    )
    __Session_create(tmp_vars)
