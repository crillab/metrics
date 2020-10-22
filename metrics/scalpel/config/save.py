###############################################################################
#                                                                             #
#  Scalpel - A Metrics Module                                                 #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                #
#  -------------------------------------------------------------------------- #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  sCAlPEL - extraCting dAta of exPeriments from softwarE Logs                #
#                                                                             #
#                                                                             #
#  This program is free software: you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation, either version 3 of the License, or (at your #
#  option) any later version.                                                 #
#                                                                             #
#  This program is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                       #
#  See the GNU General Public License for more details.                       #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this program.                                                   #
#  If not, see <https://www.gnu.org/licenses/>.                               #
#                                                                             #
###############################################################################


"""
This module provides tools for saving as YAML the configuration of Scalpel.
These tools are intended to be used when the
"""


from metrics.scalpel.config.config import IScalpelConfigurationBuilder


class ScalpelConfigurationBuilderSaveDecorator(IScalpelConfigurationBuilder):

    def __init__(self, decorated: IScalpelConfigurationBuilder):
        self._decorated = decorated
        self._dict_config = {}

    def _get_mapping(self):
        pass

    def read_mapping(self):
        pass

    def read_metadata(self):
        pass

    def read_setup(self):
        pass

    def build(self):
        pass

    def _get_campaign_name(self):
        pass

    def _get_campaign_date(self):
        pass

    def _get_os_description(self):
        pass

    def _get_cpu_description(self):
        pass

    def _get_total_memory(self):
        pass

    def _get_time_out(self):
        pass

    def _get_memory_out(self):
        pass

    def read_experiment_wares(self):
        pass

    def read_input_set(self):
        pass

    def read_source(self):
        pass

    def _get_campaign_path(self):
        pass

    def _get_format(self):
        pass

    def _guess_directory_format(self):
        pass

    def _guess_regular_format(self):
        pass

    def _guess_format(self):
        pass

    def read_csv_configuration(self):
        pass

    def _has_header(self):
        pass

    def _quote_char(self):
        pass

    def _separator(self):
        pass

    def _get_hierarchy_depth(self):
        pass

    def _get_experiment_ware_depth(self):
        pass

    def _get_custom_parser(self):
        pass

    def _get_data_files(self):
        pass

    def read_data(self):
        pass

    def _get_file_name_meta(self):
        pass

    def _get_raw_data(self):
        pass

    def _log_data(self, key, value):
        pass
