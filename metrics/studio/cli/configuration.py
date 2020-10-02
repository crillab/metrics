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
from typing import Any

from yaml import safe_load

from metrics.studio.cli.interactive import InteractiveMode


class AbstractPlotConfiguration:
    pass


class PlotConfiguration(AbstractPlotConfiguration):
    """
    The PlotConfiguration describes ....
    """

    def __init__(self, **plot_config: dict):
        self.__dict__.update(plot_config)

    def __str__(self):
        return str(self.__dict__)


class EmptyPlotConfiguration(AbstractPlotConfiguration):
    pass


class PlotConfigurationBuilder:
    """
     The PlotConfigurationBuilder allows to build plot's configuration.
     """

    def __init__(self):
        self._plot_config = {}

    def build(self) -> PlotConfiguration:
        """
         Build the PlotConfiguration object
        """
        return PlotConfiguration(**self._plot_config) if self._plot_config != {} else EmptyPlotConfiguration()

    def __setitem__(self, key: str, value: Any) -> None:
        self._plot_config[key] = value


class PlotConfigurationParser:
    """
        The PlotConfigurationParser
    """

    def __init__(self, builder: PlotConfigurationBuilder, plot_configuration):
        self._builder = builder
        self._plot_config = plot_configuration

    def parse(self) -> PlotConfiguration:
        """

        @return:
        """
        if self._plot_config:
            self._builder = YamlParser(self._plot_config).parse_config(self._builder)
        # else:
        #     self._builder = InteractiveParser().parse_config(self._builder)
        return self._builder.build()


class YamlParser:
    """
        The YamlParser
    """

    def __init__(self, plot_config_stream):
        self.plot_config = plot_config_stream

    def parse_config(self, builder: PlotConfigurationBuilder) -> PlotConfigurationBuilder:
        """

        @param builder:
        @return:
        """
        dic = safe_load(self.plot_config)
        for k, v in dic.items():
            builder[k] = v
        return builder


class InteractiveParser:
    """
        The InteractiveParser
    """

    def parse_config(self, builder: PlotConfigurationBuilder) -> PlotConfigurationBuilder:
        """
        This method parse the configuration from a beautiful command line interface.
        @param builder: A builder for create a PlotConfiguration object.
        @return: The PlotConfigurationBuilder updated
        """
        return InteractiveMode(builder).create_question().prompt()
