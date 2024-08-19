###############################################################################
#                                                                             #
#  Studio - A Metrics Module                                                  #
#  Copyright (c) 2019-2022 - Univ Artois & CNRS, Exakis Nelite                #
#  -------------------------------------------------------------------------- #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  STUdIO - uSer inTerface for bUilding experIment repOrts                    #
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
#  See the GNU Lesser General Public License for more details.                #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this program.                                                   #
#  If not, see <https://www.gnu.org/licenses/>.                               #
#                                                                             #
###############################################################################


"""
This module provides classes for building experiment reports based on Jupyter
Notebooks templates.
"""


from typing import Any, Dict

from metrics.studio.common import TemplateBuilder


class ReportBuilder(TemplateBuilder):
    """
    The ReportBuilder provides a convenient interface for creating the different
    files needed to build the report for a campaign.
    """

    def __init__(self, root_dir: str = '.') -> None:
        """
        Creates a new report builder.

        :param root_dir: The directory in which to build the report.
        """
        super().__init__(root_dir)
        self._has_runtime_analysis = False
        self._has_optim_analysis = False

    def add_load_experiments(self, notebook_name: str = 'load_experiments') -> None:
        """
        Adds the Jupyter Notebook allowing to load experiment data from the campaign.

        :param notebook_name: The name of the notebook to add.
        """
        notebook_source = 'load_experiments.ipynb'
        if self._has_optim_analysis:
            notebook_source = 'load_experiments_optim.ipynb'
        elif self._has_runtime_analysis:
            notebook_source = 'load_experiments_sat.ipynb'
        self._write_template(notebook_source, f'{notebook_name}.ipynb')

    def add_runtime_analysis(self, notebook_name: str = 'runtime_analysis') -> None:
        """
        Adds the Jupyter Notebook allowing to perform a runtime analysis of the experiment-wares
        run during the campaign.

        :param notebook_name: The name of the notebook to add.
        """
        self._has_runtime_analysis = True
        self._write_template('runtime_analysis.ipynb', f'{notebook_name}.ipynb')

    def add_optim_analysis(self, notebook_name: str = 'optim_analysis') -> None:
        """
        Adds the Jupyter Notebook allowing to perform an optimization analysis of the
        experiment-wares run during the campaign.

        :param notebook_name: The name of the notebook to add.
        """
        self._has_optim_analysis = True
        self._write_template('optim_analysis.ipynb', f'{notebook_name}.ipynb')

    def update_vars(self, variables: Dict[str, Any]) -> None:
        """
        Updates the values of some items that should be rendered in a template.

        :param variables: The items to update and their new values.
        """
        self._template_vars.update(variables)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets the value of an item that should be rendered in a template.

        :param key: The name of the value to set.
        :param value: The value to set.
        """
        self._template_vars[key] = value

    def __getitem__(self, item: str) -> Any:
        """
        Gives the value of an item that should be rendered in a template.

        :param item: The name of the value to get.

        :return: The value associated with the given name.
        """
        return self._template_vars[item]
