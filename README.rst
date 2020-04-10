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

2. Make sure that ``py.test``, ``tox`` and ``pre-commit`` are installed::

    $ pip install -r requirements-testing.txt

3. Install ``pre-commit`` hook in the local repository:

    $ pre-commit install

4. Test locally with ``py.test``::

    $ pytest -vv .

   To see the coverage use:

    $ pytest -v --cov=grass_session --cov-report=html .

   To test with different version of python or grass use:

    $ GRASSBIN=~/.local/bin/grassXX PYTHONPATH="`pwd`:$PYTHONPATH" pytest .

5. Test against multiple Python environments using ``tox``::

    $ tox
    ...
    _______________________ summary _____________________________
    py27: commands succeeded
    py36: commands succeeded
    py37: commands succeeded
    py38: commands succeeded
    congratulations :)
