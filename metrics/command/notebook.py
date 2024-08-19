###############################################################################
#                                                                             #
#  Metrics - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  Copyright (c) 2019-2024 - Univ Artois & CNRS, Luxembourg University        #
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
import os


def fill_parser(subparser) -> None:
    """
    Adds the 'notebook' command to the parser.
    """
    _ = subparser.add_parser("notebook", aliases=["n", "jupyter", "ju", "book"],
                             help="'notebook' command launches a jupyter notebook.")


def _notebook(root_directory: str = '.') -> None:
    """
    Runs Jupyter Notebook inside the root directory of the report.

    :param root_directory: The root directory of the report.
    """
    os.system(f'jupyter notebook --notebook-dir="{root_directory}"')


def manage_command(args):
    """
    Launches a Jupyter Notebook.
    """
    _notebook(os.getcwd())
