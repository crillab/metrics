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
Metrics-Studio (STUdIO - uSer inTerface for bUilding experIment repOrts)
provides convenient user interfaces for building experiment reports with Metrics,
for instance using Jupyter Notebooks.
"""
import os.path

import loguru
from jinja2 import Environment, PackageLoader, select_autoescape

from metrics.common.util import get_cache_ew_config_file
from metrics.studio.campaign import CampaignModel
from metrics.studio.database import db
from metrics.studio.report import ReportBuilder


def init_metrics_studio():
    loguru.logger.info("Creating database...")
    db.create_tables([CampaignModel], safe=True)
    ew_config_file = get_cache_ew_config_file()
    if not os.path.exists(ew_config_file):
        env = Environment(loader=PackageLoader('metrics'), autoescape=select_autoescape())
        with open(ew_config_file, 'w') as file:
            template = env.get_template("ew.yaml")
            print(template.render({}), file=file)
