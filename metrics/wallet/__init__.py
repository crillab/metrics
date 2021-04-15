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
import pickle

from metrics.wallet.analysis import Analysis, find_best_cpu_time_input
from metrics.core.constants import *

import pandas as pd
import jsonpickle.ext.pandas as jsonpickle_pd

jsonpickle_pd.register_handlers()


def import_bin_analysis(str) -> Analysis:
    return pickle.loads(str)


def import_analysis_from_file(filename) -> Analysis:
    with open(filename, 'rb') as file:
        if filename.split('.')[-1] == 'csv':
            return Analysis(data_frame=pd.read_csv(file))
        return pickle.load(file)
