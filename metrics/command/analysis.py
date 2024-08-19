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
from typing import Dict, Any

from metrics.studio import ReportBuilder
from metrics.studio.campaign import CampaignBuilder


def fill_parser(subparser):
    parser_command_analysis = subparser.add_parser("analysis",
                                                   help="'analysis' command allows to create different notebook for "
                                                        "our analysis.")
    parser_command_analysis.add_argument('--load', help='flag for adding the loading notebook',
                                         action='store_true')
    parser_command_analysis.add_argument('--load-notebook', help='the name for the loading notebook',
                                         default='load_experiments')
    parser_command_analysis.add_argument('--runtime', help='flag for adding the runtime notebook',
                                         action='store_true')
    parser_command_analysis.add_argument('--runtime-notebook', help='the name for the runtime notebook',
                                         default='runtime_analysis')
    parser_command_analysis.add_argument('--optimization',
                                         help='flag for adding the optimization notebook',
                                         action='store_true')
    parser_command_analysis.add_argument('--optimization-notebook',
                                         help='the name for the optimization notebook',
                                         default='optim_analysis')


def _create_notebook(arguments: Dict[str, Any]) -> None:
    """
    Initializes a new report directory.
    """
    campaign = CampaignBuilder(arguments['root_directory'])
    campaign.load_current_campaign()
    report = ReportBuilder(arguments['root_directory'])
    report.update_vars(arguments)
    report.update_vars(campaign.get_template_vars())

    if arguments['optimization']:
        report.add_optim_analysis(arguments['optimization_notebook'])
    if arguments['runtime']:
        report.add_runtime_analysis(arguments['runtime_notebook'])
    if arguments['load']:
        report.add_load_experiments(arguments['load_notebook'])


def manage_command(args):
    """
    Initializes a new analysis by creating the notebooks.
    """
    _create_notebook(args)
