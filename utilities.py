# This file contains functions and classes which can be classified as utilitie functions for a more
# general purpose. Furthermore, this functions are for python analysis for ALIBAVA files.

__version__ = 0.1
__date__ = "13.12.2018"
__author__ = "Dominic Bloech"
__email__ = "dominic.bloech@oeaw.ac.at"

# Import statements
import os
from tqdm import tqdm
import h5py
import yaml
import numpy as np
import matplotlib as plt


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

if __name__ == "__main__":
    li = import_h5(r"\\HEROS\dbloech\Alibava_measurements\VC811929\Pedestal.hdf5")
