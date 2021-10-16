pl-ageatscan
==============


Abstract
--------

A ChRIS app to take two CSV columns containing dates and finds the difference between them. Appends a new column containing the difference in days or months.

Description
-----------

``ageatscan`` takes two CSV columns containing dates and finds the difference between them. Appends a new column containing the difference in days or months.
Currently, the plugin only takes in CSV files directly inside /incoming. No idea if nested folders work.

Input file structure:
.. code::

	/incoming
		|---> scan.csv
		|---> scan2.csv

Outputs with the same name.
Output file structure:
.. code::

	/outgoing
		|---> scan.csv
		|---> scan2.csv

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

