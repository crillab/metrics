# ##############################################################################
#                                                                              #
#  Studio (CLI) - A Metrics Module
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                 #
#  --------------------------------------------------------------------------  #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity  #
#  sTUdIO - inTerface for bUilding experIment repOrts                          #
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
#                                                                              #
# ##############################################################################

from argparse import FileType, ArgumentParser, Namespace


def parse_args(args) -> Namespace:
    """
    Create the parser for parsing the command line.
    @return: The arparse.ArgumentPaser object.
    """
    parser = ArgumentParser(description='sTUdIO - inTerface for bUilding experIment repOrts.')

    parser.add_argument('-i', '--input', type=str, required=True,
                        help='The input file if the file is a JSON file or the YAML scalpel configuration.')
    parser.add_argument('-p', '--plot-config', type=FileType('r'), required=False)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--from-json', action='store_true',
                       help='If this option is used then the input file is json.')
    group.add_argument('--from-yaml', action='store_false',
                       help='If this option is used then the input file is not a json file but a yaml parser '
                            'configuration file')

    parser.add_argument('-w', '--web-report', required=False, action='store_true',
                        help='With this option we generate the campaign object and upload it to metrics-server. We '
                             'generate a unique link for view the report.')
    parser.add_argument('-s', '--server', required=False, default='http://crillab-metrics.cloud',
                        help='With this option we generate the campaign object and upload it to metrics-server. We '
                             'generate a unique link for view the report.')

    return parser.parse_args(args)
