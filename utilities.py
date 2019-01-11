# This file contains functions and classes which can be classified as utilitie functions for a more
# general purpose. Furthermore, this functions are for python analysis for ALIBAVA files.

__version__ = 0.1
__date__ = "13.12.2018"
__author__ = "Dominic Bloech"
__email__ = "dominic.bloech@oeaw.ac.at"

# Import statements
import os
import sys
from tqdm import tqdm
import h5py
import yaml
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from numba import jit, guvectorize, int64, float64

def create_dictionary(file, filepath):
    '''Creates a dictionary with all values written in the file using yaml'''

    file_string = os.path.abspath(os.getcwd() + str(filepath) + "\\" + str(file))
    print ("Loading file: " + str(file))
    with open(file_string, "r") as yfile:
        dict = yaml.load(yfile)
        return dict

def import_h5(*pathes):
    """
    This functions imports hdf5 files generated by ALIBAVA.
    If you pass several pathes, then you get list of objects back, containing the data respectively
    :param pathes: pathes to the datafiles which should be imported
    :return: list
    """

    # Check if a list was passed
    if type(pathes[0]) == list:
        pathes = pathes[0]

    # First check if pathes exist and if so import
    loaded_files = []
    try:
        for path in tqdm(pathes, desc= "Loading files:"):
            if os.path.exists(os.path.normpath(path)):
                # Now import all hdf5 files
                loaded_files.append(h5py.File(os.path.normpath(path), 'r'))
            else:
                raise Exception('The path {!s} does not exist.'.format(path))
        return loaded_files
    except OSError as e:
        print("Enountered an OSerror: {!s}".format(e))
        return False

def get_xy_data(data, header=0):
    """This functions takes a list of strings, containing a header and xy data, return values are 2D np.array of the data and the header lines"""

    np2Darray = np.zeros((len(data)-int(header),2), dtype=np.float32)
    for i, item in enumerate(data):
        if i > header-1:
            list_data = list(map(float,item.split()))
            np2Darray[i-header] = np.array(list_data)
    return np2Darray

def read_file(filepath):
    """Just reads a file and returns the content line by line"""
    if os.path.exists(os.path.normpath(filepath)):
        with open(os.path.normpath(filepath), 'r') as f:
            read_data = f.readlines()
        return read_data
    else:
        print("No valid path passed: {!s}".format(filepath))
        return None

def clustering(self, estimator):
    """Does the clustering up to the max cluster number, you just need the estimator and its config parameters"""
    return estimator

def count_sub_length(ndarray):
    """This function count the length of sub elements (depth 1) in the ndarray and returns an array with the lengthes
    with the same dimension as ndarray"""
    results = np.zeros(len(ndarray))
    for i in range(len(ndarray)):
        if len(ndarray[i]) == 1:
            results[i] = len(ndarray[i][0])
    return results

#@jit
def convert_ADC_to_e(signal, interpolation_function):
    """
    Gets the signal in ADC and the interpolatrion function and returns an array with the interpolated singal in electorns
    :param signal: Singnal array which should be converted, basically the singal from every strip
    :param interpolation_function: the interpolation function
    :return: Returns array with the electron count
    """
    return interpolation_function(np.abs(signal))

def save_all_plots(name, folder, figs=None, dpi=200):
    """
    This function saves all generated plots to a specific folder with the defined name in one pdf
    :param name: Name of output
    :param folder: Output folder
    :param figs: Figures which you want to save to one pdf (leaf empty for all plots) (list)
    :param dpi: image dpi
    :return: None
    """
    try:
        pp = PdfPages(os.path.normpath(folder) + "\\" + name + ".pdf")
    except PermissionError:
        print("While overwriting the file {!s} a permission error occured, please close file if opened!".format(name + ".pdf"))
        return
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in tqdm(figs, desc="Saving plots"):
        fig.savefig(pp, format='pdf')
    pp.close()

class NoStdStreams(object):
    """Surpresses all output of a function when called with with """
    def __init__(self,stdout = None, stderr = None):
        self.devnull = open(os.devnull,'w')
        self._stdout = stdout or self.devnull or sys.stdout
        self._stderr = stderr or self.devnull or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.devnull.close()


def langau_cluster(size, valid_events_Signal, valid_events_clusters,valid_events_clustersize, charge_cal, noise):
    # for size in tqdm(cluster_list, desc="(langau) Processing clustersize"):
    # get the events with the different clustersizes
    cls_ind = np.nonzero(valid_events_clustersize == size)[0]
    # indizes_to_search = np.take(valid_events_clustersize, cls_ind) # TODO: veeeeery ugly implementation
    totalE = np.zeros(len(cls_ind))
    totalNoise = np.zeros(len(cls_ind))
    # Loop over the clustersize to get total deposited energy
    incrementor = 0
    for ind in tqdm(cls_ind, desc="(langau) Processing event"):
        # TODO: make this work for multiple cluster in one event
        # Signal calculations
        signal_clst_event = np.take(valid_events_Signal[ind], valid_events_clusters[ind][0])
        totalE[incrementor] = np.sum(convert_ADC_to_e(signal_clst_event, charge_cal))

        # Noise Calculations
        noise_clst_event = np.take(noise, valid_events_clusters[ind][0])  # Get the Noise of an event
        totalNoise[incrementor] = np.sqrt(np.sum(convert_ADC_to_e(noise_clst_event, charge_cal)))  # eError is a list containing electron signal noise

        incrementor += 1

    preresults = {}
    preresults["signal"] = totalE
    preresults["noise"] = totalNoise
    return preresults
