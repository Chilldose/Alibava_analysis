"""Noise analysis of ALiBaVa files"""
# pylint: disable=C0103, R0902

import logging
from time import time
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from tqdm import tqdm
from analysis_classes.nb_analysis_funcs import nb_noise_calc
from analysis_classes.utilities import import_h5, gaussian, read_binary_Alibava
#from analysis_classes.utilities import manage_logger

class NoiseAnalysis:
    """This class contains all calculations and data concerning pedestals in
	ALIBAVA files"""

    def __init__(self, path="", configs=None, logger = None):
        """
        :param path: Path to pedestal file
        """
        self.log = logger or logging.getLogger(__class__.__name__)
        self.configs = configs
        self.median_noise = None
        #manage_logger(self.log)

        # Init parameters
        self.log.info("Loading pedestal file: {!s}".format(path))
        if not configs["isBinary"]:
            self.data = import_h5(path)[0]
        else:
            self.data = read_binary_Alibava(path)

        if self.data:
            # Some of the declaration may seem unecessary but it clears things up when you need to know how big some arrays are
            # self.data=self.data[0]# Since I always get back a list
            self.numchan = len(self.data["events"]["signal"][0])
            self.numevents = len(self.data["events"]["signal"])
            self.pedestal = np.zeros(self.numchan, dtype=np.float32)
            self.noise = np.zeros(self.numchan, dtype=np.float32)
            # Only use events with good timing, here always the case
            self.goodevents = np.nonzero(self.data["events"]["time"][:] >= 0)
            self.CMnoise = np.zeros(len(self.goodevents[0]), dtype=np.float32)
            self.CMsig = np.zeros(len(self.goodevents[0]), dtype=np.float32)
            self.score = np.zeros((len(self.goodevents[0]), self.numchan), dtype=np.float32)



            # Calculate pedestal
            self.log.info("Calculating pedestal and Noise...")
            self.pedestal = np.mean(self.data["events"]["signal"][:], axis=0)
            self.signal = np.array(self.data["events"]["signal"][:], dtype=np.float32)

            start = time()
            self.score_raw, self.CMnoise, self.CMsig = nb_noise_calc(self.signal[:],
                                                                     self.pedestal[:])

            # Calculate the actual noise for every channel by building the mean of all
            # noise from every event
            self.noise = np.std(self.score_raw,axis=0)
            self.noisy_strips, self.good_strips = self.detect_noisy_strips(self.noise, configs.get("Noise_cut", 5.))

            # Mask chips of alibava
            self.chip_selection, self.masked_channels = self.mask_alibava_chips(self.configs.get("Chips", (1,2)))
            self.good_strips = np.intersect1d(self.chip_selection, self.good_strips)

            # Redo the noise calculation but this time without the noisy strips
            self.score, self.CMnoise, self.CMsig = nb_noise_calc(self.signal[:, self.good_strips],
                                                                 self.pedestal[self.good_strips])
            self.noise_corr = np.std(self.score, axis=0)
            self.total_noise = np.concatenate(self.score, axis=0)
            end = time()
            self.log.warning("Time taken for noise calculation: {!s} seconds".format(round(abs(end - start), 2)))
        else:
            self.log.warning("No valid file, skipping pedestal run")

    def mask_alibava_chips(self, chips_to_keep=(1,2)):
        """Defines which chips should be considered"""
        final_channels = np.array([], dtype=np.int)
        for chip in chips_to_keep:
            start = (chip-1)*128
            to_keep = np.arange(start, start+128, dtype=np.int)
            final_channels = np.append(final_channels, to_keep)

        # No find the masked channels
        channels = np.arange(self.configs.get("Maximum_channels", 256), dtype=np.int)
        return final_channels, np.setdiff1d(channels, final_channels)


    def detect_noisy_strips(self, Noise, Noise_cut):
        """This function detects noisy strips and returns two arrays first
        array noisy strips, second array good strips"""

        good_strips = np.arange(len(Noise))
        # Calculate the
        self.median_noise = np.median(Noise)
        high_noise_strips = np.nonzero(Noise > self.median_noise + Noise_cut)[0]
        high_noise_strips = np.append(high_noise_strips, self.configs.get("Manual_mask", []))
        good_strips = np.delete(good_strips, high_noise_strips)

        return np.array(high_noise_strips, dtype=np.int32), np.array(good_strips, dtype=np.int32)

    def plot_data(self):
        """Plots the data calculated by the framework"""

        fig = plt.figure("Noise analysis")

        # Plot noisedata
        noise_plot = fig.add_subplot(221)
        noise_plot.bar(np.arange(self.numchan), self.noise, 1., alpha=0.4, color="b", label="Noise level per strip")
        # array of non masked strips
        valid_strips = np.ones(self.numchan)
        valid_strips[np.append(self.noisy_strips, self.masked_channels)] = 0
        noise_plot.plot(np.arange(self.numchan), valid_strips, color="r", label="Masked strips")

        # Plot the threshold for deciding a good channel
        xval = [0, self.numchan]
        yval = [self.median_noise + self.configs.get("Noise_cut", 5.),
                self.median_noise + self.configs.get("Noise_cut", 5.)]
        noise_plot.plot(xval, yval, "r--", color="g", label="Threshold for noisy strips")

        noise_plot.set_xlabel('Channel [#]')
        noise_plot.set_ylabel('Noise [ADC]')
        noise_plot.set_title('Noise levels per Channel')
        noise_plot.legend()

        # Plot pedestal
        pede_plot = fig.add_subplot(222)
        pede_plot.bar(np.arange(self.numchan), self.pedestal, 1., yerr=self.noise,
                      error_kw=dict(elinewidth=0.2, ecolor='r', ealpha=0.1), alpha=0.4, color="b")
        pede_plot.set_xlabel('Channel [#]')
        pede_plot.set_ylabel('Pedestal [ADC]')
        pede_plot.set_title('Pedestal levels per Channel with noise')
        pede_plot.set_ylim(bottom=min(self.pedestal) - 50.)
        # pede_plot.legend()

        # Plot Common mode
        CM_plot = fig.add_subplot(223)
        n, bins, patches = CM_plot.hist(self.CMnoise, bins=50, density=True, alpha=0.4, color="b")
        # Calculate the mean and std
        mu, std = norm.fit(self.CMnoise)
        # Calculate the distribution for plotting in a histogram
        p = norm.pdf(bins, loc=mu, scale=std)
        CM_plot.plot(bins, p, "r--", color="g", label='mu=' + str(round(mu, 2)) +  "\n" +
                                                      'sigma=' + str(round(std, 2)))

        CM_plot.set_xlabel('Common mode [ADC]')
        CM_plot.set_ylabel('[%]')
        CM_plot.set_title('Common mode Noise')
        CM_plot.legend()

        # Plot noise hist
        NH_plot = fig.add_subplot(224)
        n, bins, patches = NH_plot.hist(self.total_noise, bins=500, density=False, alpha=0.4, color="b")
        NH_plot.set_yscale("log", nonposy='clip')
        #NH_plot.set_yscale("log")
        NH_plot.set_ylim(1.)

        # Cut off noise part
        cut = np.max(n) * 0.2  # Find maximum of hist and get the cut
        ind = np.concatenate(np.argwhere(n > cut))  # Finds the first element which is higher as threshold optimized

        # Calculate the mean and std
        mu, std = norm.fit(bins[ind])
        # Calculate the distribution for plotting in a histogram
        plotrange = np.arange(-35, 35)
        p = gaussian(plotrange, mu, std, np.max(n))
        NH_plot.plot(plotrange, p, "r--", color="g",label='mu=' + str(round(mu, 2)) +  "\n" +
                                                      'sigma=' + str(round(std, 2)))

        NH_plot.set_xlabel('Noise')
        NH_plot.set_ylabel('count')
        NH_plot.set_title("Noise Histogram")
        NH_plot.legend()

        fig.tight_layout()
        # plt.draw()
