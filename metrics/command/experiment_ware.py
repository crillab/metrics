import argparse
import os.path
import sys

import loguru
import pandas as pd
from rich.console import Console
from rich.table import Table

from metrics.common.util import unknown_command, ChangeDirectory
from metrics.studio.campaign import CampaignBuilder
from metrics.studio.constant import METRICS_DIR_EXPERIMENT_WARE


def fill_parser(subparser):
    parser_ew = subparser.add_parser("experiment_ware", aliases=["ew", "s", "solver"],
                                     help="experiment_ware' for creating, listing, running and removing variant of the binaries added to the campaign.")
    parser_ew_subparser = parser_ew.add_subparsers(dest="subcommand")
    add_parser = parser_ew_subparser.add_parser("add")
    add_parser.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                            default=".")
    add_parser.add_argument('binary', help='ID of the binary')
    add_parser.add_argument('name', help='Name of the variant.')
    add_parser.add_argument('remainder', nargs=argparse.REMAINDER, help='Arguments for the subcommand')

    list_parser = parser_ew_subparser.add_parser("list")
    list_parser.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                             default=".")

    remove_parser = parser_ew_subparser.add_parser("remove")
    remove_parser.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                               default=".")
    remove_parser.add_argument('--binary', help='ID of the binary')
    remove_parser.add_argument('--name', help='Name of the variant.')

    run_parser = parser_ew_subparser.add_parser("run")
    run_parser.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                            default=".")
    run_parser.add_argument('--name', help='Name of the variant.')
    run_parser.add_argument('--instance', help='Path to the instance file.')
    run_parser.add_argument('--run-solver', action='store_true')




def list_command(args):
    path_xp_wares_csv = os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE, "xpwares.csv")
    if not os.path.exists(path_xp_wares_csv):
        loguru.logger.error("Path 'xpwares.csv' not exists.")
        sys.exit(1)
    table = Table(title="Experimentwares List")
    table.add_column("Binary", justify="right")
    table.add_column("Name", justify="right")
    table.add_column("Options", justify="right")

    df = pd.read_csv(path_xp_wares_csv, sep=";")
    for index, row in df.iterrows():
        table.add_row(row["id"], row["name"], row["options"])
    console = Console()
    console.print(table)


def add_command(args):
    d = {"binary": [args["binary"]], "name": [args["name"]], "options": [" ".join(args["remainder"])]}
    df_tmp = pd.DataFrame(d)
    path_xp_wares_csv = os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE, "xpwares.csv")
    if not os.path.exists(path_xp_wares_csv):
        df = df_tmp
    else:
        df = pd.read_csv(path_xp_wares_csv, sep=";")
        df = pd.concat([df, df_tmp])

    df.to_csv(path_xp_wares_csv, sep=';', index=False)

def remove_command(args):
    path_xp_wares_csv = os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE, "xpwares.csv")
    if not os.path.exists(path_xp_wares_csv):
        loguru.logger.error("Path 'xpwares.csv' not exists.")
        sys.exit(1)
    df = pd.read_csv(path_xp_wares_csv, sep=";")
    nb_rows = len(df)
    query = []
    if "binary" in args and args["binary"] is not None:
        query.append(f"binary!='{args['binary']}'")
    if "name" in args and args["name"] is not None:
        query.append(f"name!='{args['name']}'")
    q = " | ".join(query)
    loguru.logger.debug(q)
    filter_df = df.query(q)
    nb_rows2 = len(filter_df)
    loguru.logger.info(f"We remove {nb_rows - nb_rows2} experimentwares.")
    filter_df.to_csv(path_xp_wares_csv, sep=';', index=False)


def run_command(args):
    # allez lire les infos cpu_time etc de campaign.yml
    with ChangeDirectory(args.get("campaign_dir")):
        campaign_builder = CampaignBuilder(root_dir=os.getcwd())
        c = campaign_builder.load_current_campaign()
        path_xp_wares_csv = os.path.join(METRICS_DIR_EXPERIMENT_WARE, "xpwares.csv")
        if not os.path.exists(path_xp_wares_csv):
            loguru.logger.error("Path 'xpwares.csv' not exists.")
            sys.exit(1)
        df = pd.read_csv(path_xp_wares_csv, sep=";")
        experiment_ware = df.query(f"name=='{args['name']}'")
        if len(experiment_ware) == 0:
            loguru.logger.error(f"Experimentware '{args['name']}' not found.")
            sys.exit(1)
        experiment_ware = experiment_ware.iloc[0]
        experiment_ware_dir = os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE, experiment_ware["id"])
        loguru.logger.info(f"Running experimentware '{args['name']}'")

        if args["run_solver"]:
            pass


MAP_COMMAND = {
    "list": list_command,
    "add": add_command,
    "remove": remove_command,
    "run": run_command
}


def manage_command(args):
    """
    Manage the command for the experiment_ware subcommand.
    """
    subcommand = args['subcommand']
    MAP_COMMAND.get(subcommand, unknown_command)(args)
