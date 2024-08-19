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

import loguru
import pandas as pd

from metrics.common.util import unknown_command, get_cache_dir, ChangeDirectory, walk_through_files
from metrics.studio.constant import METRICS_DIR_INPUT_SET
from metrics.studio.instance import InstanceDownloader, CompositeInstanceDownloader, XCSPDownloader, XCSPFilter


def fill_parser(subparser):
    # command instances
    parser_command_instances = subparser.add_parser("instances", help="instances command")
    parser_command_instances_subcommands = parser_command_instances.add_subparsers(dest="subcommand")

    ## command download of instances

    parser_command_instances_download = parser_command_instances_subcommands.add_parser('download')
    parser_command_instances_download.add_argument("-u", "--url", help="The url for downloading files.")
    parser_command_instances_download.add_argument("-f", "--file", help="A path or an url to a file that "
                                                                        "contains one url by line.")
    ## command xcsp of instances

    parser_command_instances_xcsp = parser_command_instances_subcommands.add_parser('xcsp')
    parser_command_instances_xcsp.add_argument("-y", "--year", type=int, default=-1,
                                               help="Specify the year of the XCSP competition.", nargs='+')
    parser_command_instances_xcsp.add_argument('-t', '--types', choices=['cop', 'csp', 'minicsp', 'minicop', 'all'],
                                               default='all', help="Specify the type of instances. ")
    parser_command_instances_xcsp.add_argument("--no-global-constraint", action='store_true')
    parser_command_instances_xcsp.add_argument("-e", "--exclude", nargs='+')
    parser_command_instances_xcsp.add_argument("-i", "--include", nargs='+')
    parser_command_instances_xcsp.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                                               default=".")

    ## command collect of instances

    parser_command_instances_collect = parser_command_instances_subcommands.add_parser('collect')
    parser_command_instances_collect.add_argument("--extensions", help="Extension file to collect", nargs="+",
                                                  default=["xml", "xml.lzma"])
    parser_command_instances_collect.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                                                  default=".")
    # parser_command_instances_collect.add_argument("--campaign-directory",
    #                                               help="HPC campaign directory. If not specified, the value in the "
    #                                                    "'campaign.yml' file will be used. If the file does not exist, "
    #                                                    "the value must be specified. ")
    ## command sat of instances

    parser_command_instances_sat = parser_command_instances_subcommands.add_parser("sat")
    parser_command_instances_sat.add_argument("--gbd", nargs="+", help="One or multiple path to database files.")
    parser_command_instances_sat.add_argument("--url", help="Base url for downloading instances file",
                                              default="https://benchmark-database.de/file/")
    parser_command_instances_sat.add_argument("--query", help="Valid gbd query.")


def instances_download_file(url):
    InstanceDownloader(url).download()


def instances_download_list_files(file):
    CompositeInstanceDownloader(file).download()


def download(arguments):
    loguru.logger.info("Downloading instances...")
    if arguments.get('url') is not None:
        instances_download_file(arguments.get('url'))
    if arguments.get('file') is not None:
        instances_download_list_files(arguments.get('file'))


def xcsp(arguments):
    xcsp_cache = os.path.join(get_cache_dir(), "cache", "xcsp")
    xcsp_metadata = os.path.join(get_cache_dir(), "cache", "xcsp", "metadata")
    loguru.logger.info("Downloading instances in cache directory...")
    XCSPDownloader(arguments.get('year'), xcsp_cache).download()

    XCSPFilter(xcsp_cache, xcsp_metadata, arguments).filter().copy()


def collect(arguments):
    all_files = []
    loguru.logger.info("Collecting instances...")
    with ChangeDirectory(os.path.join(arguments.get("campaign_dir"), METRICS_DIR_INPUT_SET)):
        for extension in arguments["extensions"]:
            for file in walk_through_files(".", [extension]):
                loguru.logger.info(f"Collecting {file}...")
                # 'category': os.path.dirname(file).split('/')[-1],
                all_files.append(
                    {'problem': os.path.basename(file).split(".")[0],
                     'model_data_file': os.path.join(METRICS_DIR_INPUT_SET, os.path.basename(file))})
        df = pd.DataFrame(all_files)
        df.to_csv("instances.csv", index=False, sep=',')


def sat(arguments):
    try:
        from gbd_core.api import GBD
        if os.environ.get("GBD_DB") is None and arguments["gbd"] is None:
            loguru.logger.error(
                "Please specify the GBD_DB environment variable or add the cli argument '--gbd path1 path2'")
        paths = arguments["gbd"] or os.environ.get("GBD_DB").split(",")
        with GBD(paths) as gbd:
            df = gbd.query(arguments["query"])
            CompositeInstanceDownloader(base_url=arguments["url"]).download(list_of_files=df["hash"].values,
                                                                            extension=".cnz.xz")
    except ImportError as e:
        loguru.logger.error("Could not import gbd_core.api. Please install with 'pip install gbd-tools'. ")


MAP_COMMANDS = {
    'download': download,
    'xcsp': xcsp,
    'collect': collect,
    'sat': sat
}


def manage_command(args):
    subcommand = args['subcommand']
    MAP_COMMANDS.get(subcommand, unknown_command)(args)
