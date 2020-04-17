#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 18:36:22 2017

@author: pietro
"""
from __future__ import print_function

import atexit
import os
import shutil
import subprocess
import sys
import tempfile as tmpfile

if sys.version_info[0] >= 3:
    from shutil import which
else:
    # lazy import
    from glob import glob

    def which(cmd):
        # Fallback if default GRASS bin has not been found
        platform = get_platform_name()
        path_env = os.environ.get("PATH")
        path_sep = os.pathsep
        grassbins = []
        for dir in path_env.split(path_sep):
            grass_on_path = glob(os.path.join(dir, cmd))
            if len(grass_on_path) > 0:
                for fpath in grass_on_path:
                    if is_executable(fpath, platform):
                        grassbins.append(os.path.split(fpath)[1])

        if len(grassbins) > 0:
            grassbins.sort()
            grassbin = grassbins[-1]
            return grassbin


ORIGINAL_ENV = os.environ.copy()


def get_platform_name():
    """Return an identification string with the platform name, raise
    an exception if the platform is unknown/unsupported."""

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


def is_executable(fpath, platform):
    """Returns true if the path 'fpath' points to an executable file.
    For Windows only .py, .exe, and .bat are treated as accepted executables."""
    if os.access(fpath, os.X_OK) and os.path.isfile(fpath):
        if platform == "win32":
            win_execs = ["py", "bat", "exe"]
            if "." in fpath:
                if fpath.split(".")[-1].lower() in win_execs:
                    is_exec = True
                else:
                    is_exec = False
        else:
            is_exec = True
    else:
        is_exec = False
    return is_exec


def get_grass_bin(version=None):
    """Return the path to the GRASS GIS binary file command.
    If available takes the value from os.environ GRASSBIN variable,
    else the GRASS binary found by which (only Python 3) or the latest GRASS
    executable on the path."""
    version = "" if not version else version
    grassbin = os.environ.get("GRASSBIN")
    if grassbin:
        return grassbin

    grassbin_path = which("grass{}".format(version))
    if grassbin_path:
        grassbin = os.path.split(grassbin_path)[1]
        return grassbin

    if not grassbin:
        raise RuntimeError(
            (
                "Cannot find GRASS GIS start script: 'grass{}', "
                "set the right one using the GRASSBIN environm. "
                "variable"
            ).format(version)
        )


def get_grass_gisbase(grassbin=None):
    """Return the GRASS GISBASE path"""
    grassbin = get_grass_bin() if grassbin is None else grassbin
    cmd = "{grassbin} --config path".format(grassbin=grassbin)
    proc = subprocess.Popen(
        cmd,
        shell=True,
        env=ORIGINAL_ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    if proc.returncode != 0:
        print("cmd:", cmd)
        print("out:", out)
        print("err:", err)
        proc = subprocess.Popen(
            cmd,
            shell=True,
            env=ORIGINAL_ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        raise RuntimeError(
            (
                "Cannot find GRASS GIS start script: {grassbin}, "
                "set the right one using the GRASSBIN environm. "
                "variable"
            ).format(grassbin=grassbin)
        )
    gisbase = out.decode().strip()
    if not os.path.exists(gisbase):
        raise RuntimeError(
            (
                "GRASS GIS start script: {cmd}, "
                "return as GISBASE a directory ({gisbase}) that do not exist."
            ).format(cmd=cmd, gisbase=gisbase)
        )
    return gisbase


def set_grass_path_env(gisbase=None, env=None, grassbin=None):
    """Return a dictionary with the modified environmental variables."""
    env = os.environ if env is None else env
    gisbase = gisbase if gisbase else get_grass_gisbase(grassbin=grassbin)
    # Set GISBASE environment variable
    env["GISBASE"] = gisbase

    grass_bin = os.path.join(gisbase, "bin")
    if "PATH" in env:
        if grass_bin not in env["PATH"]:
            env["PATH"] += os.pathsep + grass_bin
    else:
        env["PATH"] = grass_bin

    if os.path.join(gisbase, "scripts") not in env["PATH"]:
        env["PATH"] += os.pathsep + os.path.join(gisbase, "scripts")

    # add path to GRASS addons
    home = os.path.expanduser("~")
    if os.path.join(home, ".grass7", "addons", "scripts") not in env["PATH"]:
        env["PATH"] += os.pathsep + os.path.join(home, ".grass7", "addons", "scripts")

    pyversion = sys.version_info[0]

    platform = get_platform_name()
    if platform == "win32":
        config_dirname = "GRASS7"
        config_dir = os.path.join(os.getenv("APPDATA"), config_dirname)
        if os.path.join(gisbase, "extrabin") not in env["PATH"]:
            env["PATH"] += os.pathsep + os.path.join(gisbase, "extrabin")
        env["GRASS_PYTHON"] = env.get("GRASS_PYTHON", "python{}.exe".format(pyversion))
        env["GRASS_SH"] = os.path.join(gisbase, "msys", "bin", "sh.exe")
    else:
        config_dirname = ".grass7"
        config_dir = os.path.join(home, config_dirname)
        env["GRASS_PYTHON"] = env.get("GRASS_PYTHON", "python{}".format(pyversion))

    addon_base = os.path.join(config_dir, "addons")
    env["GRASS_ADDON_BASE"] = addon_base
    if os.path.join(addon_base, "bin") not in env["PATH"]:
        env["PATH"] += os.pathsep + os.path.join(addon_base, "bin")
    if platform != "win32":
        if os.path.join(addon_base, "scripts") not in env["PATH"]:
            env["PATH"] += os.pathsep + os.path.join(addon_base, "scripts")

    # define LD_LIBRARY_PATH
    ld_path = os.path.join(gisbase, "lib")
    if "LD_LIBRARY_PATH" not in env:
        env["LD_LIBRARY_PATH"] = ld_path
    else:
        if env["LD_LIBRARY_PATH"] == "":
            env["LD_LIBRARY_PATH"] = ld_path
        elif ld_path not in env["LD_LIBRARY_PATH"]:
            env["LD_LIBRARY_PATH"] += os.pathsep + ld_path

    # define GRASS-Python path variable
    pypath = env.get("PYTHONPATH", "")
    grasspy = os.path.join(gisbase, "etc", "python")
    if grasspy not in pypath:
        env["PYTHONPATH"] = pypath + os.pathsep + grasspy if pypath else grasspy
    if grasspy not in sys.path:
        sys.path.insert(0, grasspy)

    env["LANG"] = "en_US.UTF-8"
    env["LOCALE"] = "en_US.UTF-8"
    env["LC_ALL"] = "en_US.UTF-8"
    return env


def clean_grass_path_env(gisbase=None, env=None, grassbin=None):
    """Remove GRASS version related variables from the environment."""
    env = os.environ if env is None else env
    gisbase = gisbase if gisbase else get_grass_gisbase(grassbin=grassbin)

    grass_bin = os.path.join(gisbase, "bin")
    # Remove from PATH
    env["PATH"] = env["PATH"].replace(os.pathsep + grass_bin, "")
    env["PATH"] = env["PATH"].replace(os.pathsep + os.path.join(gisbase, "scripts"), "")

    # Remove from LD_LIBRARY_PATH
    ld_path = os.path.join(gisbase, "lib")
    env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"].replace(os.pathsep + ld_path, "")

    # Remove from PYTHONPATH
    grasspy = os.path.join(gisbase, "etc", "python")
    env["PYTHONPATH"] = env["PYTHONPATH"].replace(grasspy, "")
    env["PYTHONPATH"] = env["PYTHONPATH"].replace(os.pathsep + os.pathsep, os.pathsep)
    return env


def write_gisrc(gisdb, location, mapset):
    """Write the ``gisrc`` file and return its path."""
    gisrc = tmpfile.mktemp()
    with open(gisrc, "w") as rc:
        rc.write(
            "GISDBASE: {}\nLOCATION_NAME: {}\nMAPSET: {}"
            "\n".format(gisdb, location, mapset)
        )
    return gisrc


def grass_init(gisbase, gisdb, location, mapset="PERMANENT", env=None, loadlibs=False):
    """Initialize system variables to run GRASS modules

    This function is for running GRASS GIS without starting it
    explicitly. No GRASS modules shall be called before call of this
    function but any module or user script can be called afterwards
    as if it would be called in an actual GRASS session. GRASS Python
    libraries are usable as well in general but the ones using
    C libraries through ``ctypes`` are not (which is caused by
    library path not being updated for the current process
    which is a common operating system limitation).

    To create a (fake) GRASS session a ``gisrc`` file is created.
    Caller is responsible for deleting the ``gisrc`` file.

    Basic usage::

        # ... setup GISBASE and PYTHON path before import
        import grass.script as gscript
        gisrc = gscript.setup.init("/usr/bin/grass7",
                                   "/home/john/grassdata",
                                   "nc_spm_08", "user1")
        # ... use GRASS modules here
        # remove the session's gisrc file to end the session
        os.remove(gisrc)

    :param gisbase: path to GRASS installation
    :param dbase: path to GRASS database (default: '')
    :param location: location name (default: 'demolocation')
    :param mapset: mapset within given location (default: 'PERMANENT')

    :returns: path to ``gisrc`` file (to be deleted later)
    """
    env = os.environ if env is None else env
    if "GISBASE" not in env:
        raise RuntimeError(
            "GRASS paths are not set, `GISBASE` is missing! "
            "Use `set_grass_path` before calling `grass_init`."
        )
    env["GIS_LOCK"] = str(os.getpid())

    # Set GISDBASE environment variable
    env["GISDBASE"] = gisdb
    # TODO: should we check if the gisdb, location and mapset are valid?
    # permanent = os.listdir(os.path.join(gisdb, location, "PERMANENT"))
    # mapset = os.listdir(os.path.join(gisdb, location, mapset))
    if loadlibs:
        load_libs(env["GISBASE"])
    env["GISRC"] = write_gisrc(gisdb, location, mapset)
    return env


def grass_create(grassbin, path, create_opts):
    """Create a new location/mapset"""
    cmd = "{grassbin} -c {create_opts} -e {path}" "".format(
        grassbin=grassbin, create_opts=create_opts, path=path
    )
    proc = subprocess.Popen(
        cmd,
        shell=True,
        env=ORIGINAL_ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            "Cannot create: {path} with the following "
            "options: {create_opts}. Executing:\n{cmd}\n"
            "GRASS said:\n"
            "{out}\n{err}".format(
                path=path, create_opts=create_opts, cmd=cmd, out=out, err=err
            )
        )


def load_libs(gisbase=None):
    # lazy import
    from glob import glob
    import ctypes

    # define LD_LIBRARY_PATH
    gisbase = os.environ["GISBASE"] if not gisbase else gisbase
    if not gisbase:
        raise RuntimeError("No gisbase supplied!")
    ld_path = os.path.join(gisbase, "lib")
    lib_suffix = "dll" if sys.platform == "win32" else "so"
    print("Loading libraries from {}".format(ld_path))
    remains = []
    grasslibs = glob("{}{}*.{}".format(ld_path, os.path.sep, lib_suffix))
    if len(grasslibs) == 0:
        raise RuntimeError("No GRASS GIS libraries found in {}.".format(ld_path))
    for lib in grasslibs:
        try:
            ctypes.CDLL(lib, mode=1)
        except Exception:
            remains.append(lib)

    tries_max = len(remains)
    tries = 1
    while len(remains) > 0 and tries < tries_max:
        tries += 1
        for lib in remains:
            try:
                ctypes.CDLL(lib, mode=1)
                remains.remove(lib)
            except Exception as exc:
                if tries == tries_max:
                    print(exc)

    if len(remains) > 0:
        raise RuntimeError(
            "Cannot load all the following GRASS GIS libraries from {}!".format(remains)
        )


class Session(object):
    def __init__(self, grassversion=None, grassbin=None, env=None, *aopen, **kwopen):
        """Create a GRASS GIS session.

        Parameters
        ----------
        grassversion : string
            Default GRASS GIS stable version
        grassbin : path
            Path to the GRASS binary file
        mapset : string
            Mapset name
        env : dict
            Dictionary to set environmental variable for the session

        Examples
        --------
        >>> import os
        >>> import tempfile
        >>> tmpdir = tempfile.mkdtemp()
        >>> with Session(gisdb=TMPDIR, location="loc", mapset="mset",
        ...              create_opts="EPSG:3035") as sess:
        ...     print("\nPROJ")
        ...     print(parse_command("g.proj", flags="g"))

        """
        self.env = os.environ if env is None else env
        self.grassbin = (
            get_grass_bin(version=grassversion) if grassbin is None else grassbin
        )
        self.gisbase = get_grass_gisbase(grassbin=self.grassbin)
        self.env = set_grass_path_env(gisbase=self.gisbase, env=self.env)
        self._aopen = aopen
        self._kwopen = kwopen

    def open(
        self, gisdb, location, mapset=None, create_opts=None, env=None, loadlibs=False
    ):
        """Open or create GRASS GIS mapset.

        Parameters
        ----------
        gisdb : string, path-like
            Path to the GISDB directory
        location : string
            Location name
        mapset : string
            Mapset name
        create_opts : string
            Valid string for the grass `-c` flag
            (`[-c | -c geofile | -c EPSG:code[:datum_trans] | -c XY]`)
        env : dict
            Dictionary to set environmental variable for the session

        Examples
        --------
        Create a new location and mapset

        >>> import os
        >>> import tempfile
        >>> tmpdir = tempfile.mkdtemp()
        >>> sess = Session()
        >>> sess.open(gisdb=TMPDIR, location="loc", mapset="mset",
        ...           create_opts="EPSG:3035")
        >>> print("\nPROJ")
        >>> print(parse_command("g.proj", flags="g"))
        >>> sess.close()

        """
        env = self.env if env is None else env
        mapset = "PERMANENT" if mapset is None else mapset
        lpath = os.path.join(gisdb, location)
        mpath = os.path.join(gisdb, location, mapset)
        if create_opts is not None:
            if mapset == "PERMANENT" and not os.path.exists(lpath):
                path = lpath
            else:
                path = mpath
            self.create(path, create_opts=create_opts)
        return grass_init(
            self.gisbase, gisdb, location, mapset, env=env, loadlibs=loadlibs
        )

    def create(self, path, create_opts):
        """Create a new mapset

        Parameters
        ----------
        path : string, path-like
            Path to gisdb/location/mapset
        create_opts : string
            Valid string for the grass `-c` flag
            (`[-c | -c geofile | -c EPSG:code[:datum_trans] | -c XY]`)

        See an example in `Session.open()` method.
        """
        grass_create(self.grassbin, path, create_opts)

    def close(self):
        """Close a GRASS Session."""
        if "GISRC" in self.env:
            self.env.pop("GIS_LOCK")
            os.remove(self.env.pop("GISRC"))

        self.env = clean_grass_path_env(
            gisbase=self.gisbase, env=self.env, grassbin=None
        )

    def __enter__(self):
        self.open(*self._aopen, **self._kwopen)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class TmpSession(Session):
    """Create a temporary session. The session is removed at the program exit.
    """

    def __init__(self, *args, **kwargs):
        self.created_path = None
        super(TmpSession, self).__init__(*args, **kwargs)

    def create(self, path, create_opts):
        """Create a new temporary location/mapset.
        """
        self.created_path = path
        grass_create(self.grassbin, path, create_opts)
        atexit.register(self.close)

    def close(self):
        """Close a GRASS Session."""
        if "GISRC" in self.env:
            self.env.pop("GIS_LOCK")
            os.remove(self.env.pop("GISRC"))

        self.env = clean_grass_path_env(
            gisbase=self.gisbase, env=self.env, grassbin=None
        )
        if self.created_path is not None:
            shutil.rmtree(self.created_path)
            self.created_path = None


# set path when importing the library
GRASSBIN = get_grass_bin()
GISBASE = get_grass_gisbase(grassbin=GRASSBIN)
set_grass_path_env(GISBASE, env=os.environ, grassbin=GRASSBIN)


if __name__ == "__main__":
    grassbin = get_grass_bin()
    gisbase = get_grass_gisbase(grassbin=grassbin)
    env = set_grass_path_env(gisbase=gisbase, env=os.environ)
