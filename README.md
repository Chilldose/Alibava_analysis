### Alibava_analysis

This software was developed by Dominic Blöch during his Phd Thesis at the
HEPHY Vienna. It is intended to analyse Alibava Systems hdf5 files.
It feautures a basic clustering analysis as well as Langau fitting to the
energy deposition of events

### Getting Started

In order to run this program you need a Python Anaconda distribution. For
more information on versions see Chapter "What you need". Anaconda will install
its own python environment, which is called "base". You can run Anaconda from
its private console or integrate it in your OS console.

For Windows (Powershell):

* Add "Anaconda3/Scripts/" to your PATH
* Open Powershell and enable external scripts by entering
    ```
    set-executionpolicy remotesigned
    ```
* You should now be able to see the Anaconda environment

### Setting Up The Environement

With Anaconda and console set up, you enter the "Alibava_analysis" folder
and create a new environment by entering

```
conda env create -f requirements.yml
```

this will also automatically install all required modules for the program to
run. If you don't have Anaconda installed and don't want to use it, you can
check the "requirements.yml" file to see what dependencies the program needs.

### Running The Program

Adjust the "default_config.yml" file in "Examples" to uýour needs and add the
respective file paths of pedestal, calibration and main measurement run. Now it
should be possible to run the program by:

```
python main.py --config <path_to_config YAML file>
```

### How to Use

In the future here will be a Link to the docs or something else

### What you need

* The program is known to be running on Windows, Linux (Centos7) and Mac.
* Python
    You need python >= 3.6 (64 bit distribution). 32 bit works as well
    but unstable.
* Anaconda
    [Anaconda](https://www.anaconda.com/download/) python distribution, it will
    work with a normal version too, but it's not tested.
* Microsoft Visual C++
    [Microsoft Visual C++ 14.0](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
    Required for PyLandau package
* Important packages
    * [Numba](http://numba.pydata.org/) - For Low-Level optimizations
    * [Numpy](http://www.numpy.org/) - For numerical operations
    * [SciPy](https://www.scipy.org/) - For numerical operations
    * [Matplotlib](https://matplotlib.org/) - For the plots
    * [PyLandau](https://github.com/SiLab-Bonn/pylandau) - For Langau fitting


## Authors

* **Dominic Blöch** - *Initial work* - [Chilldose](https://github.com/Chilldose)
* **Marius Metzler** - *Developer*

## License

This project is licensed under the GNU License - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* Thanks to my friends for their inspiring conversations and help
