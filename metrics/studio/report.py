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


import os

from typing import Any, Dict

from jinja2 import Environment, PackageLoader
from jinja2 import select_autoescape


class ReportBuilder:
    """
    The ReportBuilder provides a convenient interface for creating the different
    files needed to build the report for a campaign.
    """

    def __init__(self, root_dir: str = '.') -> None:
        """
        Creates a new report builder.

        :param root_dir: The directory in which to build the report.
        """
        self._root_dir = root_dir
        self._template_vars = {}
        self._env = Environment(loader=PackageLoader('metrics'), autoescape=select_autoescape())

    def create_directories(self) -> None:
        """
        Creates the directories needed for the report.
        """
        if not os.path.exists(self._root_dir):
            os.mkdir(self._root_dir)

        for name in ('config', 'experiment_wares', 'experiments', 'input_set'):
            path = os.path.join(self._root_dir, name)
            if not os.path.exists(path):
                os.mkdir(path)

    def install(self) -> None:
        """
        Installs Metrics' dependencies in the current environment.
        """
        os.system('pip3 install crillab-metrics jupyter')

    def git_init(self) -> None:
        """
        Initializes a git repository inside the report directory.
        """
        os.system(f'git init "{self._root_dir}"')
        self._write_template('gitignore', '.gitignore')

    def add_readme(self) -> None:
        """
        Adds a README file to the report.
        """
        self._write_template('README.md', 'README.md')

    def add_requirements(self) -> None:
        """
        Adds the requirements file to the report (i.e., the file listing all the dependencies
        that should be installed to execute the report).
        """
        self._write_template('requirements.txt', 'requirements.txt')

    def add_scalpel_config(self, config_name: str = 'scalpel_config') -> None:
        """
        Adds Scalpel's configuration to the report.

        :param config_name: The name of Scalpel's configuration file.
        """
        self._write_template('scalpel_config.yml', os.path.join('config', f'{config_name}.yml'))

    def add_load_experiments(self, notebook_name: str = 'load_experiments') -> None:
        """
        Adds the Jupyter Notebook allowing to load experiment data from the campaign.

        :param notebook_name: The name of the notebook to add.
        """
        self._write_template('load_experiments.ipynb', f'{notebook_name}.ipynb')

    def add_runtime_analysis(self, notebook_name: str = 'runtime_analysis') -> None:
        """
        Adds the Jupyter Notebook allowing to perform a runtime analysis of the experiment-wares
        run during the campaign.

        :param notebook_name: The name of the notebook to add.
        """
        self._write_template('runtime_analysis.ipynb', f'{notebook_name}.ipynb')

    def add_optim_analysis(self, notebook_name: str = 'optim_analysis') -> None:
        """
        Adds the Jupyter Notebook allowing to perform an optimization analysis of the
        experiment-wares run during the campaign.

        :param notebook_name: The name of the notebook to add.
        """
        self._write_template('optim_analysis.ipynb', f'{notebook_name}.ipynb')

    def _write_template(self, template_name: str, output_file: str) -> None:
        """
        Writes a report file following a template.

        :param template_name: The name of the file to use as template.
        :param output_file: The path of the output file (relative to the root directory of
                            the report).
        """
        with open(os.path.join(self._root_dir, output_file), 'w') as file:
            template = self._env.get_template(template_name)
            print(template.render(**self._template_vars), file=file)

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
