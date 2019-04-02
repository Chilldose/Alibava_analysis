"""PlotData Class"""
# pylint: disable=R0201,C0103
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from analysis_classes.utilities import handle_sub_plots, gaussian

class PlotData:
    """This class contains all calculations and data concerning pedestals in
	ALIBAVA files"""
    def __init__(self):
        # canvas for plotting the data [width, height (inches)]
        self.fig = plt.figure("Noise analysis", figsize=[10, 8])

        self.ped_plots = [self.plot_noise_ch, self.plot_pedestal, self.plot_cm,
                          self.plot_noise_hist]
        self.cal_plots = [self.plot_scan, self.plot_gain_hist,
                          self.plot_gain_strip]

    def plot_data(self, obj, group="all", show=True):
        """Plots the data calculated by the framework. Surpress drawing and
        showing the canvas by setting "show" to False.
        Returns matplotlib.pyplot.figure object.
        """
        if group == "pedestal":
            for func in self.ped_plots:
                func(obj, self.fig)
        elif group == "calibration":
            for func in self.cal_plots:
                func(obj, self.fig)
        self.fig.tight_layout()
        if show:
            plt.draw()
            plt.show()
        return self.fig

    ### Pedestal Plots ###
    def plot_noise_ch(self, obj, fig=None):
        """plot noise per channel"""
        noise_plot = handle_sub_plots(fig, 221)
        noise_plot.bar(np.arange(obj.numchan), obj.noise, 1.,
                       alpha=0.4, color="b", label="Noise level per strip")
        # plot line idicating masked and unmasked channels
        valid_strips = np.ones(obj.numchan)
        valid_strips[obj.noisy_strips] = 0
        noise_plot.plot(np.arange(obj.numchan), valid_strips, color="r",
                        label="Masked strips")

        # Plot the threshold for deciding a good channel
        xval = [0, obj.numchan]
        yval = [obj.median_noise + obj.noise_cut,
                obj.median_noise + obj.noise_cut]
        noise_plot.plot(xval, yval, "r--", color="g",
                        label="Threshold for noisy strips")

        noise_plot.set_xlabel('Channel [#]')
        noise_plot.set_ylabel('Noise [ADC]')
        noise_plot.set_title('Noise levels per Channel')
        noise_plot.legend(loc='upper right')
        return noise_plot

    def plot_pedestal(self, obj, fig=None):
        """Plot pedestal and noise per channel"""
        pede_plot = handle_sub_plots(fig, 222)
        pede_plot.bar(np.arange(obj.numchan), obj.pedestal, 1., yerr=obj.noise,
                      error_kw=dict(elinewidth=0.2, ecolor='r', ealpha=0.1),
                      alpha=0.4, color="b", label="Pedestal")
        pede_plot.set_xlabel('Channel [#]')
        pede_plot.set_ylabel('Pedestal [ADC]')
        pede_plot.set_title('Pedestal levels per Channel with noise')
        pede_plot.set_ylim(bottom=min(obj.pedestal) - 50.)
        pede_plot.legend(loc='upper right')
        return pede_plot

    def plot_cm(self, obj, fig=None):
        """Plot the common mode distribution"""
        plot = handle_sub_plots(fig, 223)
        _, bins, _ = plot.hist(obj.CMnoise, bins=50, density=True,
                               alpha=0.4, color="b", label="Common mode")
        # Calculate the mean and std
        mu, std = norm.fit(obj.CMnoise)
        # Calculate the distribution for plotting in a histogram
        p = norm.pdf(bins, loc=mu, scale=std)
        plot.plot(bins, p, "r--", color="g", label="Fit")
        plot.set_xlabel('Common mode [ADC]')
        plot.set_ylabel('[%]')
        plot.set_title(r'$\mathrm{Common\ mode\:}\ \mu=' + str(round(mu, 2)) \
                       + r',\ \sigma=' + str(round(std, 2)) + r'$')
        plot.legend(loc='upper right')
        return plot

    def plot_noise_hist(self, obj, fig=None):
        """Plot total noise distribution. Find an appropriate Gaussian while
        excluding the "ungaussian" parts of the distribution"""
        plot = handle_sub_plots(fig, 224)
        n, bins, _ = plot.hist(obj.total_noise, bins=500, density=False,
                               alpha=0.4, color="b", label="Noise")
        plot.set_yscale("log", nonposy='clip')
        plot.set_ylim(1.)

        # Cut off "ungaussian" noise
        cut = np.max(n) * 0.2  # Find maximum of hist and get the cut
        # Finds the first element which is higher as optimized threshold
        ind = np.concatenate(np.argwhere(n > cut))

        # Calculate the mean and std
        mu, std = norm.fit(bins[ind])
        # Calculate the distribution for plotting in a histogram
        plotrange = np.arange(-35, 35)
        p = gaussian(plotrange, mu, std, np.max(n))
        plot.plot(plotrange, p, "r--", color="g", label="Fit")
        plot.set_xlabel('Noise')
        plot.set_ylabel('count')
        plot.set_title("Noise Histogram")
        return plot

    ### Calibration Plots ###
    def plot_scan(self, obj, fig):
        """Plot delay or charge scan"""
        if not obj.configs["use_charge_cal"]:
            plot = fig.add_subplot(222)
            plot.bar(obj.delay_data["scan"]["value"][:],
                     obj.meansig_delay, 1., alpha=0.4, color="b")
            # plot.bar(obj.delay_data["scan"]["value"][:],
            #                obj.meansig_delay[:,60], 1., alpha=0.4, color="b")
            plot.set_xlabel('time [ns]')
            plot.set_ylabel('Signal [ADC]')
            plot.set_title('Delay plot')
        else:
            plot = fig.add_subplot(221)
            plot.set_xlabel('Charge [e-]')
            plot.set_ylabel('Signal [ADC]')
            plot.set_title('Charge plot')
            plot.bar(obj.charge_data["scan"]["value"][:],
                     np.mean(obj.meansig_charge, axis=1), 1000.,
                     alpha=0.4, color="b", label="Mean of all gains")
            cal_range = np.array(np.arange(1., 450., 10.))
            plot.plot(np.polyval(obj.meancoeff, cal_range),
                             cal_range, "r--", color="g")
            plot.errorbar(obj.charge_data["scan"]["value"][:],
                          np.mean(obj.meansig_charge, axis=1),
                          xerr=obj.charge_sig, yerr=obj.ADC_sig,
                          fmt='o', markersize=1, color="red",
                          label="Error")
            plot.legend()
        return plot

    def plot_gain_strip(self, obj, fig):
        """Plot gain per Strip at 100 ADC"""
        gain_plot = fig.add_subplot(223)
        gain_plot.set_xlabel('Channel [#]')
        gain_plot.set_ylabel('Gain [e- at 100 ADC]')
        gain_plot.set_title('Gain per Channel')
        gain_plot.set_ylim(0, 70000)
        gain_plot.bar(np.arange(len(obj.pedestal) - len(obj.noisy_channels)),
                      obj.gain, alpha=0.4, color="b",
                      label="Only non masked channels")
        gain_plot.legend()
        return gain_plot

    def plot_gain_hist(self, obj, fig):
        """Plot histogram of gain per strip at 100 ADC"""
        gain_hist = fig.add_subplot(224)
        gain_hist.set_ylabel('Count [#]')
        gain_hist.set_xlabel('Gain [e- at 100 ADC]')
        gain_hist.set_title('Gain Histogram')
        gain_hist.hist(obj.gain, alpha=0.4, bins=20, color="b",
                       label="Only non masked channels")
        gain_hist.legend()
        return gain_hist

    ### Analysis Plots ###