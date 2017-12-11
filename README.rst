GRASS GIS session library
=========================

A simple library to use GRASS GIS from python.
You can specify the GRASS executable that you want to use with an
enviromental variable called: `GRASSBIN`



Status
------

In development


Install
-------

To install the stable version use: ::

    $ pip install grass-session


To install the current development version use: ::

    $ pip install git+https://github.com/zarch/grass-session.git


Examples
--------

Set the GRASS GIS binary that you want to use with:
`export GRASSBIN=grass75`::

    >>> from grass_session import Session
    >>> from grass.script import core as gcore
    >>> with Session(gisdb="/tmp", location="location",
    ...              create_opts="EPSG:4326"):
    ...    print(gcore.parse_command("g.gisenv", flags="s"))
    {u'GISDBASE': u"'/tmp/';",
     u'LOCATION_NAME': u"'epsg3035';",
     u'MAPSET': u"'PERMANENT';",}
    >>> with Session(gisdb="/tmp", location="location", mapset="test",
    ...              create_opts=""):
    ...    print(gcore.parse_command("g.gisenv", flags="s"))
    {u'GISDBASE': u"'/tmp/';",
     u'LOCATION_NAME': u"'epsg3035';",
     u'MAPSET': u"'test';",}


Development
-----------

1. Clone the repository::

    $ git clone git@github.com:zarch/grass_session.git

2. Make sure that ``py.test``, and ``tox`` are installed::

    $ pip install -r requirements-testing.txt

3. Test locally with ``py.test``::

    $ py.test test/

5. Test against multiple Python environments using ``tox``::

    $ tox
    ...
    _________________________________ summary _________________________________
    py27: commands succeeded
    py36: commands succeeded
    congratulations :)
