# ##############################################################################
#                                                                              #
#  Studio (CLI) - A Metrics Module
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                 #
#  --------------------------------------------------------------------------  #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity  #
#  sTUdIO - inTerface for bUilding experIment repOrts                          #
#                                                                              #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify it     #
#  under the terms of the GNU Lesser General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or (at your  #
#  option) any later version.                                                  #
#                                                                              #
#  This program is distributed in the hope that it will be useful, but         #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY  #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                        #
#  See the GNU General Public License for more details.                        #
#                                                                              #
#  You should have received a copy of the GNU Lesser General Public License    #
#  along with this program.                                                    #
#  If not, see <https://www.gnu.org/licenses/>.                                #
#                                                                              #
# ##############################################################################
from argparse import Namespace

from metrics.core.model import Campaign
from metrics.scalpel import read_campaign
from metrics.studio.cli.configuration import PlotConfiguration, PlotConfigurationParser, PlotConfigurationBuilder


class Report:
    """
    This class represent the meta object Report.
    """

    def __init__(self, plot_config: PlotConfiguration, campaign: Campaign):
        self.plot_config = plot_config
        self.campaign = campaign

    def generate_report(self):
        """
        Generate the report
        """
        pass


class ReportBuilder:
    """
        The ReportBuilder
    """

    def __init__(self, args: Namespace):
        self._args = args
        self._plot_config = None
        self._campaign = None

    def _load_input_file(self) -> 'ReportBuilder':
        """
        Load input file with scalpel module and get the campaign object
        @return: The current report object
        """

        self._campaign = read_campaign(self._args.input)
        return self

    def _load_plot_config(self) -> 'ReportBuilder':
        """
        Load the plot_config if exist
        @return: The current report object
        """
        plot_configuration_parser = PlotConfigurationParser(PlotConfigurationBuilder(), self._args.plot_config)
        self._plot_config = plot_configuration_parser.parse()
        print(self._plot_config)
        return self

    def load(self) -> 'ReportBuilder':
        """

        @return:
        """
        return self._load_input_file()._load_plot_config()

    def build(self) -> Report:
        """
        @return
        """
        return Report(self._plot_config, self._campaign)
