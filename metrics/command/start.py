###############################################################################
#                                                                             #
#  Metrics - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  Copyright (c) 2019-2024 - Univ Artois & CNRS, Exakis Nelite                #
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
from typing import Dict, Any

import loguru

from metrics.common.util import create_cache_directory, download_metadata
from metrics.studio import init_metrics_studio
from metrics.studio.campaign import CampaignBuilder


def init_metrics():
    loguru.logger.info("Initializing Metrics...")
    create_cache_directory()
    download_metadata()
    init_metrics_studio()


def fill_parser(subparser):
    parser_command_init = subparser.add_parser("start",
                                               help="Initialize a new campaign environment with necessary "
                                                    "directories, configuration files, Python environment setup, "
                                                    "and registration in the local campaign database.")

    # Registering the option used to specify the root directory for the report.
    parser_command_init.add_argument('-d', '--root-directory',
                                     help='specifies the root directory for the campaign',
                                     default=os.getcwd())
    parser_command_init.add_argument('-t', '--title',
                                     help='specifies the title for this campaign. By default the title is the name of '
                                          'the root directory.')
    parser_command_init.add_argument('--no-shell', action='store_true')


def manage_command(arguments: Dict[str, Any]):
    init_metrics()
    campaign = CampaignBuilder(arguments['root_directory'])
    if arguments.get("title") is None:
        arguments["title"] = arguments["root_directory"].split('/')[-1]
    campaign.update_vars(arguments)
    campaign.create_directories()
    campaign.install()
    campaign.git_init()
    campaign.add_readme()
    campaign.add_requirements()
    campaign.add_campaign_config()
    campaign.add_scripts()
    campaign.add_run_solver()
    campaign.register()
    if not arguments['no_shell']:
        campaign.shell()
