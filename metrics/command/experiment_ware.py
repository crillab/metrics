import argparse


def fill_parser(subparser):
    parser_ew = subparser.add_parser("experiment_ware", aliases=["ew", "s", "solver"],
                                     help="experiment_ware' for creating, listing, running and removing variant of the binaries added to the campaign.")
    parser_ew_subparser = parser_ew.add_subparsers(dest="subcommand")
    add_parser = parser_ew_subparser.add_parser("add")
    add_parser.add_argument('id', help='ID of the binary')
    add_parser.add_argument('name', help='Name of the variant.')
    add_parser.add_argument('remainder', nargs=argparse.REMAINDER, help='Arguments for the subcommand')


def list_command(args):
    pass


def add_command(args):
    pass


def remove_command(args):
    pass


MAP_COMMAND = {
    "list": list_command,
    "add": add_command,
}


def manage_command(args):
    """
    Manage the command for the experiment_ware subcommand.
    """
