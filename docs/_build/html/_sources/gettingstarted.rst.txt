.. _gettingstarted:

Getting Started
===============

In order to run this program you need a Python (Anaconda) distribution.
For more information on how to install see the :ref:`installation` guide.

If you have already installed python correctly for AliSys you can proceed with the next topic.


Creating a Config file
~~~~~~~~~~~~~~~~~~~~~~

Explain principal structure of the config


Running The Analysis
~~~~~~~~~~~~~~~~~~~~

Now it should be possible to run the program by: ::

    python main.py --config <your_config_file>

    >>> 2019-04-23 11:32:02,705 - INFO - NoiseAnalysis - Loading pedestal file: C:\Pedestal.hdf5
    >>> 2019-04-23 11:32:02,716 - INFO - NoiseAnalysis - Calculating pedestal and Noise...
    >>> 2019-04-23 11:32:03,989 - INFO - Calibration - Loading charge calibration file: C:\charge.h5
    >>> ...

If you are getting some errors you most likely made a mistake with the config file.
Alisys tries to tell you what it does not like on you config file and you should be able to solve the issues with that in no time.
We tried to make the error output as intuitive as possible and hope you can sort the problems with no efforts =).

