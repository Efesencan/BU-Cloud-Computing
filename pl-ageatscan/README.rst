pl-simpledsapp
==============

.. image:: https://img.shields.io/docker/v/fnndsc/pl-simpledsapp
    :target: https://hub.docker.com/r/fnndsc/pl-simpledsapp

.. image:: https://img.shields.io/github/license/fnndsc/pl-simpledsapp
    :target: https://github.com/FNNDSC/pl-simpledsapp/blob/master/LICENSE

.. image:: https://github.com/FNNDSC/pl-simpledsapp/workflows/ci/badge.svg
    :target: https://github.com/FNNDSC/pl-simpledsapp/actions


.. contents:: Table of Contents


Abstract
--------

A ChRIS app to take two CSV columns containing dates and finds the difference between them. Appends a new column containing the difference in days or months.

Description
-----------

``ageatscan`` takes two CSV columns containing dates and finds the difference between them. Appends a new column containing the difference in days or months.


Usage
-----

.. code::

        python ageatscan.py
            [-h] [--help]
            [-p <PREFIX>]
            <inputDir>
            <outputDir>
            [-u <days, mths>] [--unit <days, mths>]
	    [-v] [-verbose]
	    [-s <STRING>][--subtrahend <STRING>]
	    [-m <STRING>][--minuend <STRING>]
	    [-r <STRING>][--result <STRING>]

Arguments
~~~~~~~~

.. code::

        [-h] [--help]
        If specified, show help message and exit.

        [-v] [--verbose]
	Displays the output CSV in stdout

        <inputDir>
        Input directory.

        [-p <PREFIX>]
	The type of file. Usually '*.csv'. Defaults to '*.csv' 
  
        [-u <days, mths>] [--unit <days, mths>]
	The unit for the results column. Choose days or (months, mth, m)

        [-s <STRING>][--subtrahend <STRING>]
	Column name of the subtrahend. Defaults to 'DateOfBirth'

        [-m <STRING>][--minuend <STRING>]
	Column name of the minuend. Defaults to 'DateOfScan'

        [-r <STRING>][--result <STRING>]
	Output header name for results column. Defaults to 'AgeAtScan'
Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-simpledsapp simpledsapp --man

Run
~~

You need you need to specify input and output directories using the `-v` flag to `docker run`.


.. code:: bash

    docker run --rm -u $(id -u)                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
        fnndsc/pl-simpledsapp simpledsapp                        \
        /incoming /outgoing


Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-simpledsapp .

Run unit tests:

.. code:: bash

    docker run --rm local/pl-simpledsapp nosetests

Examples
--------

    docker run --rm -u $(id -u)                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
        fnndsc/pl-simpledsapp simpledsapp                        \
        /incoming /outgoing --prefix lolo


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
