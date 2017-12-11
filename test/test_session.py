import tempfile
import os
import shutil

import pytest

import grass_session as gs


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


@pytest.fixture(scope="module")
def tmp_vars(request):
    tmpdir = tempfile.mkdtemp()
    location_name = 'location'
    location_path = os.path.join(tmpdir, location_name)

    def finalizer():
        print("teardown")
        shutil.rmtree(location_path, ignore_errors=False)

    print("setup")
    request.addfinalizer(finalizer)
    return dict(tmpdir=tmpdir,
                location_name=location_name,
                location_path=os.path.join(tmpdir, location_name),
                create_opts="EPSG:3035",
                mapset=os.path.join(location_path, "test"),
                grassbin=gs.get_grass_bin())


class TestCreate(object):
    def test_create(self, tmp_vars):
        gs.grass_create(grassbin=tmp_vars["grassbin"],
                        path=tmp_vars["location_path"],
                        create_opts=tmp_vars["create_opts"])
        # check if PERMANENT has been created
        assert os.listdir(tmp_vars["location_path"]) == ["PERMANENT", ]

        # check files
        permanent = os.path.join(tmp_vars["location_path"], "PERMANENT")
        files = sorted(["DEFAULT_WIND", "MYNAME", "PROJ_EPSG",
                        "PROJ_INFO", "PROJ_UNITS", "sqlite", "VAR", "WIND"])
        assert sorted(os.listdir(permanent)) == files

        # check PROJ_EPSG content
        with open(os.path.join(permanent, "PROJ_EPSG"), mode="r") as prj:
            assert prj.readlines() == ['epsg: 3035\n', ]

        # check creation of a mapset
        gs.grass_create(grassbin=tmp_vars["grassbin"], path=tmp_vars["mapset"],
                        create_opts="")
        assert os.path.exists(tmp_vars["mapset"]) is True
        files = sorted(["sqlite", "VAR", "WIND"])
        assert sorted(os.listdir(tmp_vars["mapset"])) == files
