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
import os.path
import sys

import loguru

from metrics.common.util import unknown_command
from metrics.scalpel import CampaignParserListener
from metrics.scalpel.config import ScalpelConfigurationLoader
from metrics.scalpel.config.configsaver import ScalpelConfigurationWrapperSaverDecorator
from metrics.studio.campaign import CampaignBuilder
from metrics.studio.scalpelcli import CLIScalpelConfigurationWrapper


def _common_options(parser):
    group_id_name = parser.add_mutually_exclusive_group()
    group_id_name.add_argument('--id', help="The id of the campaign.")
    group_id_name.add_argument('--name', help="The name of the campaign.")

    parser.add_argument("-c", "--campaign-directory",
                        help="specifies the path to the parent folder of the campaign folder on the "
                             "runtime system (.e.g. HPC).")
    parser.add_argument("--host",
                        help="specifies the ssh hostname of HPC.")

    parser.add_argument("-p", "--port",
                        help="specifies the ssh port of HPC.", default=22)


def add_other_parsers(parser):
    _ = parser.add_parser("submit", help="The 'submit' command is "
                                         "used to submit all jobs to "
                                         "the remote scheduler. ")
    _ = parser.add_parser("status",
                          help="The 'status' command is used to check "
                               "the execution status of the current "
                               "campaign or the campaign whose name "
                               "or id is specified in the parameter. ")
    _ = parser.add_parser("cancel",
                          help="The 'cancel' command is used to cancel jobs "
                               "in a campaign. ")
    _ = parser.add_parser("list",
                          help="List all registered campaigns.")


def add_parser_upload_download(parser):
    parser_campaign_upload = parser.add_parser("upload",
                                               help="The 'upload' command is used to "
                                                    "upload the campaign from the current "
                                                    "folder to the remote campaign folder. ")
    parser_campaign_upload.add_argument("--rsync-options", default=("-h", "-a", "-v", "-z"))
    parser_campaign_download = parser.add_parser("download",
                                                 help="The 'download' command is used to "
                                                      "download the campaign from the "
                                                      "remote campaign folder to the "
                                                      "current campaign folder.")
    parser_campaign_download.add_argument("--rsync-options", default=("-h", "-a", "-v", "-z"))


def add_parser_config(parser):
    parser_campaign_config = parser.add_parser("config",
                                               help="The 'config' command is used to configure the campaign. ")
    parser_campaign_config.add_argument('--kv', nargs='+',
                                        help='Key-value pairs in the format key value (.e.g. -kv os "Ubuntu 22.04" )',
                                        action='append')


def add_parser_scalpel(parser):
    _ = parser.add_parser("scalpel",
                          help="The 'scalpel' command launches the interactive mode for configuring scalpel. ")


def _add_subcommands(parser):
    add_parser_config(parser)
    add_parser_scalpel(parser)
    add_parser_upload_download(parser)
    add_other_parsers(parser)


def fill_parser(subparser) -> None:
    parser_campaigns = subparser.add_parser("campaign", aliases=["c", "camp"],
                                            help="Campaign' command for managing the entire campaign. "
                                                 "Each 'campaigns' sub-command can be used to specify "
                                                 "the campaign id or the name to be used. It is also "
                                                 "possible to specify the campaign's remote folder, "
                                                 "the remote ssh host and the ssh port.")

    _common_options(parser_campaigns)

    parser_campaigns_subparser = parser_campaigns.add_subparsers(dest="subcommand",
                                                                 help="The sub-commands available allow you to "
                                                                      "initialise, save, download, upload, submit, "
                                                                      "check and cancel a campaign.")

    _add_subcommands(parser_campaigns_subparser)


def upload(args):
    pass


def submit(args):
    pass


def cancel(args):
    pass


def status(args):
    pass


def list(args):
    pass


def config(args):
    campaign_builder = CampaignBuilder()
    campaign_builder.load_current_campaign()
    if args.kv:
        kv_pairs = {}
        for pair in args.kv:
            for kv in pair:
                keys, value = kv.split(maxsplit=1)
                keys = keys.split('.')
                current_dict = kv_pairs
                for key in keys[:-1]:
                    current_dict = current_dict.setdefault(key, {})
                current_dict[keys[-1]] = value
        campaign_builder.update_vars(kv_pairs)
        campaign_builder.add_readme()
        campaign_builder.add_campaign_config()


def scalpel(args):
    campaign_file = os.path.join(os.getcwd(), METRICS_DIR_CONFIG, "campaign.yml")
    if not os.path.exists(campaign_file):
        loguru.logger.error("The file 'config/campaign.yml'  does not exist.")
        sys.exit(1)
    wrapper = ScalpelConfigurationWrapperSaverDecorator(CLIScalpelConfigurationWrapper(),
                                                        campaign_file)
    scalpel_config = ScalpelConfigurationLoader(wrapper, CampaignParserListener())
    scalpel_config.load()
    wrapper.save()


MAP_COMMAND = {
    "upload": upload,
    "submit": submit,
    "cancel": cancel,
    "status": status,
    "list": list,
    "config": config,
    "scalpel": scalpel
}


def manage_command(args):
    subcommand = args['subcommand']
    MAP_COMMAND.get(subcommand, unknown_command)(args)
