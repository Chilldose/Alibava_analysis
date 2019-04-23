.. _installation:

Installation
===============

What you need
~~~~~~~~~~~~~
You need a python python 3.7 64 bit distribution. (32 bit works as well but can be unstable)
I recommended to use AliSys with an Anaconda python distribution which you can download here:

`Download Anaconda here <https://www.anaconda.com/download/>`_

.. warning:: Make sure to download the 64-bit version!

it will work with a normal python version too, but I have not tested it.
Firthermore, the packages from Anaconda are optimized with other modules and you
will gain a significant performance boost using Anaconda.

Once installed, get all dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Anaconda comes with a large variety of usefull modules but this software needs
a bit more then that. Luckily I have set up an Anaconda requierements file for
you which you simply have to execute and all gets installed by itself.

.. warning:: This requirements file creates a new python 3.7 environment on your machine! Meaning it will not disturb any of your current running python distro. But you have to manually activate this env when using! You can set it as your main env as well. How to do so please read the Anaconda docs. Its not that hard ;)

First open your Anaconda Promp::

    (base) conda env create -f requirements.yml
    ...
    (base) activate AliSysenv
    (AliSysenv) python
    Python 3.7.0 |Anaconda, Inc.| (default, Dec 30 2018, 18:50:55) [MSC v.1915 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import numba


If this code does not yield any errors, the environement should be set up correctly.
And we can go on and crunch some numbers.

Download the AliSys source code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you just want the latest version download the corresponding branch from my GitHub repository.

`AliSys <https://github.com/Chilldose/Alibava_analysis>`_

There will always be a release version, which hast the latest stable running version of this software.
Once you have the version you like, continue with the :ref:`gettingstarted` section.

