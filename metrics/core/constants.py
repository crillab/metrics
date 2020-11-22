# ##############################################################################
#  Wallet - A Metrics Module                                                   #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                 #
#  --------------------------------------------------------------------------  #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity  #
#  wALLET - Automated tooL for expLoiting Experimental resulTs                 #
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
# ##############################################################################

"""
This module provides all the constants composing metrics.
"""

# Our model

## Campaign constants
CAMPAIGN_NAME = 'name'
CAMPAIGN_DATE = 'date'
CAMPAIGN_OS = 'os'
CAMPAIGN_MEMORY = 'memory'
CAMPAIGN_CPU = 'cpu'
CAMPAIGN_TIMEOUT = 'timeout'
CAMPAIGN_MEMOUT = 'memout'
CAMPAIGN_XP_WARES = 'experiment_wares'
CAMPAIGN_INPUT_SET = 'input_set'
CAMPAIGN_EXPERIMENTS = 'experiments'

## Experimentware constant
XP_WARE_NAME = 'name'

## Experiment constants
EXPERIMENT_INPUT = 'input'
EXPERIMENT_XP_WARE = 'experiment_ware'
EXPERIMENT_CPU_TIME = 'cpu_time'

## Input constants
INPUT_NAME = 'name'

## Input set constants
INPUT_SET_NAME = 'name'
INPUT_SET_INPUTS = 'inputs'

# Dataframe

SUCCESS_COL = 'success'

# Figures

## StatTable
STAT_TABLE_COUNT = 'count'
STAT_TABLE_SUM = 'sum'
STAT_TABLE_COMMON_COUNT = 'common count'
STAT_TABLE_COMMON_SUM = 'common sum'
STAT_TABLE_UNCOMMON_COUNT = 'uncommon count'
STAT_TABLE_TOTAL = 'total'
