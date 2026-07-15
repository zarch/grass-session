GRASS GIS session library
=========================

A simple library to use GRASS GIS from python.
You can specify the GRASS GIS executable that you want to use with an
enviromental variable called: `GRASSBIN`

.. note::

    **For GRASS GIS >= 8.5, the built-in approach is recommended.**

    Starting with GRASS GIS 8.5, the ``grass.script`` and ``grass.tools``
    libraries now provide first-class support for managing sessions and
    running tools programmatically. This functionality supersedes
    ``grass-session`` and is the blessed way to use GRASS GIS from Python.

    Just like ``grass-session`` relied on the ``GRASSBIN`` environment variable
    to locate GRASS, you can add the GRASS Python path to ``PYTHONPATH``
    once in your environment:

    .. code-block:: bash

        export PYTHONPATH="$PYTHONPATH:$(grass --config python_path)"

    Then your scripts can simply import and use GRASS directly:

    .. code-block:: python

        import grass.script as gs
        from grass.tools import Tools

        # Create a new project (formerly "location")
        gs.create_project(path="/tmp/my_project", epsg="4326")

        # Initialize the GRASS session
        with gs.setup.init("/tmp/my_project") as session:
            tools = Tools(session=session)
            tools.g_region(rows=100, cols=100)
            tools.r_slope_aspect(elevation="elevation", slope="slope")

    Alternatively, the ``PYTHONPATH`` can be set inline when running a script:

    .. code-block:: bash

        PYTHONPATH=$PYTHONPATH:$(grass --config python_path) python myscript.py

    For full details, please refer to the official documentation:

    - `Python intro (8.5) <https://grass.osgeo.org/grass85/manuals/python_intro.html>`_
    - `grass.tools API <https://grass.osgeo.org/grass-stable/manuals/libpython/grass.tools.html>`_

    The ``grass-session`` package remains useful for **GRASS GIS < 8.5**
    and is still maintained for backward compatibility.


Status
------

**Maintenance mode.**

This package is no longer under active development.
It is maintained for backward compatibility with **GRASS GIS < 8.5**.

Since GRASS GIS 8.5, the built-in ``grass.script`` and ``grass.tools``
libraries provide the same functionality natively (see the note above).
Once GRASS 8.5 reaches the Debian stable branch, this package will be
deprecated and archived.


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
