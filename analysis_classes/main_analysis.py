"""This file contains the main loop class that loops over the complete
run data"""
#pylint: disable=R0902,R0915,C0103,C0301

import logging
from multiprocessing import Pool
from time import time
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from .base_analysis import BaseAnalysis
from .utilities import Bdata, read_binary_Alibava, load_plugins
from .utilities import import_h5, manage_logger

class MainAnalysis:
    # COMMENT: the __init__ should be split up at least into 2 methods
    """This class analyses measurement files per event and conducts additional
    defined analysis"""
    def __init__(self, path=None, logger=None, **kwargs):
        """
        :param path_list: List of pathes to analyse
        :param kwargs: kwargs if further data should be used, possible kwargs=calibration,noise
        """

        # Init parameters
        self.log = logger or logging.getLogger(__class__.__name__)
        #manage_logger(self.log)

        if not path_list:
            self.log.info("No file to analyse passed...")
            self.outputdata = {}
            return

        self.log.info("Loading event file(s): {!s}".format(path_list))

        if not kwargs["configs"].get("isBinary", False):
            self.data = import_h5(path_list)
        else:
            self.data = read_binary_Alibava(path)

        self.numchan = len(self.data[0]["events"]["signal"][0])
        self.numevents = len(self.data[0]["events"]["signal"])
        self.pedestal = np.zeros(self.numchan, dtype=np.float32)
        self.noise = np.zeros(self.numchan, dtype=np.float32)
        self.SN_cut = 1
        self.hits = 0
        self.tmin = 0
        self.tmax = 100
        self.maxcluster = 4
        self.CMN = np.zeros(self.numchan, dtype=np.float32)
        self.CMsig = np.zeros(self.numchan, dtype=np.float32)
        self.outputdata = {}
        self.automasked_hit = 0
        self.numgoodevents = 0
        self.total_events = self.numevents * len(self.data)
        self.additional_analysis = []
        self.start = time()
        self.pathes = path_list
        self.kwargs = kwargs
        self.noise_analysis = kwargs["configs"].get("noise_analysis", None)
        self.calibration = kwargs["configs"].get("calibration", None)
        # self.kwargs = kwargs.get("configs", {}) # If a config was passeds it has to be a dict containig all settings
        # therefore kwargs rewritten

        self.pedestal = self.noise_analysis.pedestal
        self.CMN = self.noise_analysis.CMnoise
        self.CMsig = self.noise_analysis.CMsig
        self.noise = self.noise_analysis.noise
        self.SN_cut = self.kwargs["configs"]["SN_cut"]  # Cut for the signal to noise ratio

        # For additional analysis
        self.add_analysis = kwargs["configs"].get("additional_analysis", [])
        if not self.add_analysis:
            self.add_analysis = []

        # Material decision
        self.material = kwargs["configs"].get("sensor_type", "n-in-p")
        if self.material == "n-in-p":
            self.material = 1
        else:
            self.material = 0  # Easier to handle

        self.masking = kwargs["configs"].get("automasking", False)
        self.max_clustersize = kwargs["configs"].get("max_cluster_size", 5)
        self.SN_ratio = kwargs["configs"].get("SN_ratio", 0.5)
        self.usejit = kwargs["configs"].get("optimize", False)
        self.SN_cluster = kwargs["configs"].get("SN_cluster", 6)

        # Create a pool for multiprocessing
        self.process_pool = kwargs["configs"].get("Processes", 1)  # How many workers
        self.Pool = Pool(processes=self.process_pool)

        if "timing" in kwargs["configs"]:
            self.min = kwargs["configs"]["timing"][0]  # timinig window
            self.max = kwargs["configs"]["timing"][1]  # timing maximum

        self.log.info("Processing files ...")
        # Here a loop over all files will be done to do the analysis on all imported files
        for data in tqdm(range(len(self.data)), desc="Data files processed:"):
            events = np.array(self.data[data]["events"]["signal"][:], dtype=np.float32)
            timing = np.array(self.data[data]["events"]["time"][:], dtype=np.float32)

            try:
                file = str(self.data[data]).split('"')[1].split('.')[0]
            except:
                file = str(data)
            self.outputdata[file] = {}
            # Todo: Make this loop work in a pool of processes/threads whichever is easier and better
            object = BaseAnalysis(self, events,
                                   timing)  # you get back a list with events, containing the event processed data -->
                                            # np array makes it easier to slice
            results = object.run()

            self.outputdata[file]["base"] = Bdata(results,
                                                  labels=["Signal", "SN", "CMN", "CMsig", "Hitmap", "Channel_hit",
                                                          "Clusters", "Numclus", "Clustersize"])

        # Now process additional analysis statet in the config file
        # Load all plugins
        plugins = load_plugins(kwargs["configs"].get("additional_analysis",[]))

        for analysis in self.add_analysis:
            #self.log.info("\nStarting analysis: {!s}".format(analysis))
            # Gets the total analysis class, so be aware of changes inside!!!
            add_analysis = getattr(plugins[analysis], str(analysis))(self)
            results = add_analysis.run()
            add_analysis.plot()
            if results:  # Only if results have been returned
                for file in results:
                    self.outputdata[file][str(analysis)] = results[file]

        # In the end give a round up of all you have done
        print("*************************************************************************\n"
              "            Analysis report:                                             \n"
              "            ~~~~~~~~~~~~~~~~                                             \n"
              "                                                                         \n"
              "            Events processed:  {events!s}                                \n"
              "            Total events:      {total_events!s}                          \n"
              "            Time taken:        {time!s}                                  \n"
              "                                                                         \n"
              "*************************************************************************\n".format(
            automasked=self.automasked_hit,
            events=self.numgoodevents,
            total_events=self.total_events,
            time=round((time() - self.start), 1))
        )
        # Add the noise results to the final dict
        self.outputdata["noise"] = {"pedestal": self.pedestal, "cmn": self.CMN, "cmnsig": self.CMsig,
                                    "noise": self.noise}

        self.Pool.close()
        self.Pool.join()

    def plot_data(self, single_event=-1, show=True):
        """This function plots all data processed
           name (str) :
        """

        for name, data in self.outputdata.items():
            if name != "noise":
                self.plot_hitmap(name, data)
                self.plot_cluster_analysis(name, data)
                if show:
                    plt.draw()
                    plt.show()
            # Plot a single event from every file
            # if single_event > 0:
            #     self.plot_single_event(single_event, name)


    def plot_cluster_analysis(self, name, data, fig=None):
        # Plot Clustering results
        if fig is None:
            fig = plt.figure("Clustering Analysis on file: {!s}".format(name))
            numclusters_plot = fig.add_subplot(221)
            clusters_plot = fig.add_subplot(222)

        # Plot Number of clusters
        # numclusters_plot = fig.add_subplot(221)
        bins, counts = np.unique(data["base"]["Numclus"], return_counts=True)
        numclusters_plot.bar(bins, counts, alpha=0.4, color="b")
        numclusters_plot.set_xlabel('Number of clusters [#]')
        numclusters_plot.set_ylabel('Occurance [#]')
        numclusters_plot.set_title('Number of clusters')
        # numclusters_plot.set_yscale("log", nonposy='clip')

        # Plot clustersizes
        bins, counts = np.unique(np.concatenate(data["base"]["Clustersize"]), return_counts=True)
        clusters_plot.bar(bins, counts, alpha=0.4, color="b")
        clusters_plot.set_xlabel('Clustersize [#]')
        clusters_plot.set_ylabel('Occurance [#]')
        clusters_plot.set_title('Clustersizes')
        # clusters_plot.set_yscale("log", nonposy='clip')

        fig.suptitle('Cluster analysis from file {!s}'.format(name))
        fig.tight_layout()
        fig.subplots_adjust(top=0.88)

    def plot_hitmap(self, name, data, fig=None):
        # Plot Analysis results
        if fig is None:
            fig = plt.figure("Analysis file: {!s}".format(name))
            channel_plot = fig.add_subplot(111)

        # Plot Hitmap
        # channel_plot = fig.add_subplot(211)
        channel_plot.bar(np.arange(self.numchan),
                         data["base"]["Hitmap"][len(data["base"]["Hitmap"]) - 1], 1.,
                         alpha=0.4, color="b")
        channel_plot.set_xlabel('channel [#]')
        channel_plot.set_ylabel('Hits [#]')
        channel_plot.set_title('Hitmap from file: {!s}'.format(name))

        fig.tight_layout()

    def plot_single_event(self, eventnum, file):
        """ Plots a single event and its data"""

        data = self.outputdata[file]

        fig = plt.figure("Event number {!s}, from file: {!s}".format(eventnum, file))

        # Plot signal
        channel_plot = fig.add_subplot(211)
        channel_plot.bar(np.arange(self.numchan),
                         data["base"]["Signal"][eventnum], 1.,
                         alpha=0.4, color="b")
        channel_plot.set_xlabel('channel [#]')
        channel_plot.set_ylabel('Signal [ADC]')
        channel_plot.set_title('Signal')

        # Plot signal/Noise
        SN_plot = fig.add_subplot(212)
        SN_plot.bar(np.arange(self.numchan),
                    data["base"]["SN"][eventnum], 1.,
                    alpha=0.4, color="b")
        SN_plot.set_xlabel('channel [#]')
        SN_plot.set_ylabel('Signal/Noise [ADC]')
        SN_plot.set_title('Signal/Noise')

        fig.suptitle('Single event analysis from file {!s}, with event: {!s}'.format(file, eventnum))
        fig.tight_layout()
        fig.subplots_adjust(top=0.88)
        # plt.draw()
