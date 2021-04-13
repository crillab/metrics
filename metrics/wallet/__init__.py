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
import os

from metrics.wallet.dataframe.builder import Analysis

import pickle


def get_cache_or_parse(input_file, filename='.cache') -> Analysis:
    if os.path.isfile(filename) and filename is not None:
        with open(filename, 'rb') as file:
            return import_analysis_from_file(file)
    else:
        with open(filename, 'wb') as file:
            analysis = Analysis(input_file=input_file)
            analysis.export(file=file)
            return analysis


def import_analysis(str) -> Analysis:
    return pickle.loads(str)


def import_analysis_from_file(file) -> Analysis:
    return pickle.load(file)
