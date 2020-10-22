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
import json
from argparse import Namespace
from typing import Any

import jsonpickle

from metrics.core.model import Campaign
from metrics.scalpel import read_campaign
from metrics.studio.cli.configuration import PlotConfiguration, PlotConfigurationParser, PlotConfigurationBuilder


class Report:
    """
    This class represent the meta object Report.
    """

    def __init__(self, campaign: Campaign):
        self._campaign = campaign

    def generate_report(self):
        """
        Generate the report
        """
        raise NotImplementedError('Method "generate_report()" is abstract!')


class PDFReport(Report):
    def __init__(self, plot_config: PlotConfiguration, campaign: Campaign):
        self._plot_config = plot_config
        super().__init__(campaign)

    def generate_report(self):
        pass


class WebReport(Report):
    def __init__(self, campaign: Campaign, server: str):
        super().__init__(campaign)
        self._server = server
        self._json = None

    def _serialize_campaign(self) -> Any:
        j = jsonpickle.encode(self._campaign)
        json.dump(j, open('result.json', 'w'))
        return j

    def _make_request(self):
        import requests
        res = requests.post(f'{self._server}/send-campaign', json=self._json)
        if res.ok:
            result = res.json()
            print(f'Your report: {self._server}{result["url"]}')

    def generate_report(self):
        self._json = self._serialize_campaign()
        self._make_request()


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
        campaign, config = read_campaign(self._args.input)
        self._campaign = campaign
        return self

    def _load_plot_config(self) -> 'ReportBuilder':
        """
        Load the plot_config if exist
        @return: The current report object
        """
        plot_configuration_parser = PlotConfigurationParser(PlotConfigurationBuilder(), self._args.plot_config)
        self._plot_config = plot_configuration_parser.parse()
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
        if self._args.web_report:
            return WebReport(campaign=self._campaign, server=self._args.server)
        else:
            return PDFReport(self._plot_config, campaign=self._campaign)
