"""This file is the main analysis file. All processes will be started
from here"""

__version__ = 0.1
__date__ = "13.12.2018"
__author__ = "Dominic Bloech"
__email__ = "dominic.bloech@oeaw.ac.at"

import os
import sys
import matplotlib.pyplot as plt
# COMMENT: optparse is deprecated... switch to argparse
from optparse import OptionParser
from analysis_classes.calibration import Calibration
from analysis_classes.noise_analysis import NoiseAnalysis
from analysis_classes.main_loops import MainLoops
from utilities import create_dictionary, save_all_plots, save_dict


def main(args, options):
    """The main analysis which will be executed after the arguments are
    parsed"""
    # COMMENT: args unused???
    if options.configfile and os.path.exists(
            os.path.normpath(options.configfile)):
        configs = create_dictionary(os.path.normpath(options.configfile), "")
        do_with_config_file(configs)
        plt.show()

    elif options.filepath and os.path.exists(os.path.normpath(options.filepath)):
        pass

    else:
        sys.exit("No valid path parsed! Exiting")


def do_with_config_file(config):
    """Starts analysis with a config file"""

    # Look if a calibration file is specified
    if "Delay_scan" in config or "Charge_scan" in config:
        config_data = Calibration(config.get("Delay_scan", ""),
                                  config.get("Charge_scan", ""))
        config_data.plot_data()

    # Look if a pedestal file is specified
    if "Pedestal_file" in config:
        noise_data = NoiseAnalysis(config["Pedestal_file"],
                                   usejit=config.get("optimize", False),
                                   configs=config)
        noise_data.plot_data()

    # Look if a pedestal file is specified
    if "Measurement_file" in config:
        # TODO: potential call before assignment error !!! with pedestal file

        config.update({"pedestal": noise_data.pedestal,
                       "CMN": noise_data.CMnoise,
                       "CMsig": noise_data.CMsig,
                       "Noise": noise_data.noise,
                       "calibration": config_data,
                       "noise_analysis": noise_data})

        # Is a dictionary containing all keys and values for configuration
        event_data = MainLoops(config["Measurement_file"], configs=config)
        #event_data.plot_data(single_event=config.get("Plot_single_event", 15))
        # Save the plots if specified
        if config.get("Output_folder", "") and config.get("Output_name", ""):
            save_all_plots(config["Output_name"], config["Output_folder"],
                           dpi=300)
            #print("Size of output data: {!s} MB".format(get_size(event_data)/1000000.))
            if config.get("Pickle_output", False):
                save_dict(event_data.outputdata, config["Output_folder"] +
                          "\\" + config["Output_name"] + ".dba")
        plt.show()


# Parse some options to the main analysis
PARSER = OptionParser()
PARSER.add_option("--config",
                  dest="configfile", action="store", type="string",
                  help="The path to the configfile which should be read",
                  default="")
PARSER.add_option("--file",
                  dest="filepath", action="store", type="string",
                  help="Filepath of a measurement run",
                  default="")
(OPTIONS, ARGS) = PARSER.parse_args()

# try:
if __name__ == "__main__":
    main(ARGS, OPTIONS)
# except KeyError:
    #print("ERROR: I need an input file!")
# except IndexError:
    #print("ERROR: I need at least one parameter to work properly!")
