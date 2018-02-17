#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 18:36:22 2017

@author: pietro
"""
from __future__ import print_function
import os
import sys
import subprocess

import tempfile as tmpfile


DEFAULTBIN = "grass{version}"
DEFAULTGRASSBIN = dict(win32="C:\OSGeo4W\bin\grass{version}svn.bat",
                       darwin=("/Applications/GRASS/"
                               "GRASS-{version[0]}.{version[1]}.app/"))
ORIGINAL_ENV = os.environ.copy()


def get_platform_name(__cache=[None, ]):
    """Return an identification string with the platform name, raise
    an exception if the platform is unknown/unsupported."""
    def get_platform():
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
    if __cache[0] is None:
        __cache[0] = get_platform()
    return __cache[0]


def get_grass_bin(version="74"):
    """Return the path to the GRASS GIS binary file command.
    If available takes the value from os.environ GRASSBIN variable."""
    default = DEFAULTBIN.format(version=version)
    platform = get_platform_name()
    return os.environ.get('GRASSBIN', DEFAULTGRASSBIN.get(platform, default))


def get_grass_gisbase(grassbin=None):
    """Return the GRASS GISBASE path"""
    grassbin = get_grass_bin() if grassbin is None else grassbin
    cmd = "{grassbin} --config path".format(grassbin=grassbin)
    proc = subprocess.Popen(cmd, shell=True, env=ORIGINAL_ENV,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        print("cmd:", cmd)
        print("out:", out)
        print("err:", err)
        proc = subprocess.Popen(cmd, shell=True, env=ORIGINAL_ENV,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raise RuntimeError(("Cannot find GRASS GIS start script: {grassbin}, "
                            "set the right one using the GRASSBIN environm. "
                            "variable").format(grassbin=grassbin))
    return out.decode().strip()


def set_grass_path_env(gisbase=None, env=None, grassbin=None):
    """Return a dictionary with the modified environmental variables."""
    env = os.environ if env is None else env
    gisbase = gisbase if gisbase else get_grass_gisbase(grassbin=grassbin)
    # Set GISBASE environment variable
    env['GISBASE'] = gisbase

    grass_bin = os.path.join(gisbase, 'bin')
    if 'PATH' in env:
        env['PATH'] += os.pathsep + grass_bin
    else:
        env['PATH'] = grass_bin
    env['PATH'] += os.pathsep + os.path.join(gisbase, 'scripts')
    # add path to GRASS addons
    home = os.path.expanduser("~")
    env['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons',
                                             'scripts')

    platform = get_platform_name()
    if platform == "win32":
        config_dirname = "GRASS7"
        config_dir = os.path.join(os.getenv('APPDATA'), config_dirname)
        env['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
        env['GRASS_PYTHON'] = env.get('GRASS_PYTHON', "python.exe")
        env['GRASS_SH'] = os.path.join(gisbase, 'msys', 'bin', 'sh.exe')
    else:
        config_dirname = ".grass7"
        config_dir = os.path.join(home, config_dirname)
        env['GRASS_PYTHON'] = env.get('GRASS_PYTHON', "python")

    addon_base = os.path.join(config_dir, 'addons')
    env['GRASS_ADDON_BASE'] = addon_base
    env['PATH'] += os.pathsep + os.path.join(addon_base, 'bin')
    if platform != "win32":
        env['PATH'] += os.pathsep + os.path.join(addon_base, 'scripts')

    # define LD_LIBRARY_PATH
    ld_path = os.path.join(gisbase, 'lib')
    if 'LD_LIBRARY_PATH' not in env:
        env['LD_LIBRARY_PATH'] = ld_path
    else:
        env['LD_LIBRARY_PATH'] += os.pathsep + ld_path

    # define GRASS-Python path variable
    pypath = env.get('PYTHONPATH', "")
    grasspy = os.path.join(gisbase, "etc", "python")
    if grasspy not in pypath:
        env['PYTHONPATH'] = (pypath + os.pathsep + grasspy if pypath else
                             grasspy)
    if grasspy not in sys.path:
        sys.path.insert(0, grasspy)

    env['LANG'] = 'en_US.UTF-8'
    env['LOCALE'] = 'C'
    env['LC_ALL'] = 'C'
    return env


def write_gisrc(gisdb, location, mapset):
    """Write the ``gisrc`` file and return its path."""
    gisrc = tmpfile.mktemp()
    with open(gisrc, 'w') as rc:
        rc.write("GISDBASE: {}\nLOCATION_NAME: {}\nMAPSET: {}"
                 "\n".format(gisdb, location, mapset))
    return gisrc


def grass_init(gisbase, gisdb, location, mapset='PERMANENT', env=None):
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
        raise RuntimeError("GRASS paths are not set, `GISBASE` is missing! "
                           "Use `set_grass_path` before calling `grass_init`.")
    env['GIS_LOCK'] = str(os.getpid())

    # Set GISDBASE environment variable
    env['GISDBASE'] = gisdb
    # TODO: should we check if the gisdb, location and mapset are valid?
    # permanent = os.listdir(os.path.join(gisdb, location, "PERMANENT"))
    # mapset = os.listdir(os.path.join(gisdb, location, mapset))
    env['GISRC'] = write_gisrc(gisdb, location, mapset)
    return env


def grass_create(grassbin, path, create_opts):
    """Create a new location/mapset"""
    cmd = ("{grassbin} -c {create_opts} -e {path}"
           "".format(grassbin=grassbin, create_opts=create_opts,
                     path=path))
    proc = subprocess.Popen(cmd, shell=True, env=ORIGINAL_ENV,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError("Cannot create: {path} with the following "
                           "options: {create_opts}. Executing:\n{cmd}\n"
                           "GRASS said:\n"
                           "{out}\n{err}".format(path=path,
                                                 create_opts=create_opts,
                                                 cmd=cmd,
                                                 out=out, err=err))


class Session():
    def __init__(self, grassversion="74", grassbin=None, env=None,
                 *aopen, **kwopen):
        """Create a GRASS GIS session"""
        self.env = os.environ if env is None else env
        self.grassbin = (get_grass_bin(version=grassversion)
                         if grassbin is None else grassbin)
        self.gisbase = get_grass_gisbase(grassbin=self.grassbin)
        self.env = set_grass_path_env(gisbase=self.gisbase, env=self.env)
        self._aopen = aopen
        self._kwopen = kwopen

    def open(self, gisdb, location, mapset=None, create_opts=None, env=None):
        """Open or create GRASS GIS mapset."""
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
        return grass_init(self.gisbase, gisdb, location, mapset, env=env)

    def create(self, path, create_opts):
        """Create a new mapset"""
        grass_create(self.grassbin, path, create_opts)

    def close(self):
        """Close a GRASS Session."""
        if "GISRC" in self.env:
            self.env.pop("GIS_LOCK")
            os.remove(self.env.pop("GISRC"))

    def __enter__(self):
        self.open(*self._aopen, **self._kwopen)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


# set path wehn importing the library
GRASSBIN = get_grass_bin()
print("GRASSBIN:", GRASSBIN)
GISBASE = get_grass_gisbase(grassbin=GRASSBIN)
print("GISBASE:", GISBASE)
set_grass_path_env(GISBASE, env=os.environ, grassbin=GRASSBIN)


if __name__ == "__main__":
    ggrassbin = get_grass_bin()
    gisbase = get_grass_gisbase(grassbin=ggrassbin)
    env = set_grass_path_env(gisbase=gisbase, env=os.environ)
