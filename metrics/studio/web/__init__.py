# ##################################################################################################
#  Studio (WEB) - A Metrics Module                                                                 #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                                     #
#  --------------------------------------------------------------------------                      #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity                      #
#  sTUdIO - inTerface for bUilding experIment repOrts                                              #
#                                                                                                  #
#                                                                                                  #
#  This program is free software: you can redistribute it and/or modify it                         #
#  under the terms of the GNU Lesser General Public License as published by                        #
#  the Free Software Foundation, either version 3 of the License, or (at your                      #
#  option) any later version.                                                                      #
#                                                                                                  #
#  This program is distributed in the hope that it will be useful, but                             #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY                      #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                                            #
#  See the GNU General Public License for more details.                                            #
#                                                                                                  #
#  You should have received a copy of the GNU Lesser General Public License                        #
#  along with this program.                                                                        #
#  If not, see <https://www.gnu.org/licenses/>.                                                    #
# ##################################################################################################
import os

from metrics.studio.web.application import dash

if not os.path.exists('uploads'):
    os.mkdir('uploads')