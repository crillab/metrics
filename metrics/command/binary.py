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
import stat
import subprocess
import sys
from subprocess import PIPE
from urllib.parse import urlparse

import loguru
import requests
import yaml
from git import Repo
from rich.console import Console
from rich.table import Table

from metrics.common.util import unknown_command, get_cache_ew_cache_file, get_cache_ew_config_file, get_cache_ew_dir, \
    ChangeDirectory
from metrics.studio.common import TemplateBuilder
from metrics.studio.constant import METRICS_DIR_EXPERIMENT_WARE

AFTER_SH = "after.sh"
BEFORE_SH = "before.sh"
EXEC_SH = "exec.sh"
BUILD_SH = "build.sh"


class BinaryBuilder(TemplateBuilder):
    def __init__(self, root_dir):
        super().__init__(root_dir)

    def add_executable(self, executable):
        self._template_vars["executable"] = executable

    def add_parameters(self, format_parameters, included_options=None):
        if included_options is None:
            included_options = []
        parameters = format_parameters.replace("{{instance}}", "$INSTANCE").replace("{{options}}",
                                                                                    f'{included_options} "$@"' if included_options is not None else '"$@"')
        self._template_vars["parameters"] = parameters

    def add_command_prefix(self, command_prefix):
        self._template_vars["command_prefix"] = command_prefix if command_prefix is not None else ""

    def build(self, template_name, output_name):
        self._write_template(template_name, output_name)


def fill_parser(subparser) -> None:
    parser_ew = subparser.add_parser("binary", aliases=["b"],
                                     help="binary' command for managing the binaries of the campaign.")

    parser_ew_subparser = parser_ew.add_subparsers(dest="subcommand",
                                                   help="The sub-commands available allow you to "
                                                        "collect the experiment_ware of the campaign.  ")
    list_parser = parser_ew_subparser.add_parser("list",
                                                 description="This command list the binaries available for "
                                                             "this campaign.")
    list_parser.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                             default=".")

    list_parser.add_argument("--global", action="store_true",
                             help="List the binaries available globally.")

    list_parser.add_argument("-u", "--force-update", action="store_true",
                             help="Force an update of the list of binaries available globally.")

    add_parser = parser_ew_subparser.add_parser("add",
                                                description="This command integrates an experiment_ware into the existing "
                                                            "campaign. It adds the files associated with the experiment_ware "
                                                            "and updates the campaign configuration file to include settings "
                                                            "for parsing this solver.")
    add_parser.add_argument("name", help="The name of the experiment_ware.")
    add_parser.add_argument("ew_version",
                            help="The name of the version of the experiment_ware. The default value is 'latest'.",
                            default="latest")
    add_parser.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                            default=".")

    repo_parser = parser_ew_subparser.add_parser("repo",
                                                 description="This command manages the source repository of the experiment_ware.")
    repo_parser.add_argument("--url", help="The url or path to a new repository.")
    repo_parser.add_argument("--remove", help="The id of the source to remove.", type=int)

    build_parser = parser_ew_subparser.add_parser("build",
                                                  description="This command build an experiment_ware.")
    build_parser.add_argument("id", help="The id of the experiment_ware.")
    build_parser.add_argument("-c", "--campaign-dir", help="The path to the campaign directory.",
                              default=".")

    _ = parser_ew_subparser.add_parser("run",
                                       description="This command run an experiment_ware.")


def _download_file(url, download_path):
    response = requests.get(url)
    response.raise_for_status()  # Lance une exception si la requête n'a pas réussi
    with open(download_path, 'wb') as f:
        f.write(response.content)


def _clone_repo(repo_url, clone_path):
    if os.path.exists(clone_path):
        Repo.clone_from(repo_url, clone_path)
        return True
    else:
        return False


def _process_yaml_file(file_path, merged_dict):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        if 'name' in data:
            merged_dict[data['name']] = data
        else:
            loguru.logger.warning(f"No key 'name' in {file_path}")


def _handle_line(line, cache_dir):
    line = line.strip()
    if line.endswith('.yaml'):
        if line.startswith('http://') or line.startswith('https://'):
            file_name = os.path.basename(urlparse(line).path)
            download_path = os.path.join(cache_dir, file_name)
            _download_file(line, download_path)
            return download_path
        else:
            return line  # Chemin local au fichier YAML
    elif line.endswith('.git'):
        repo_name = os.path.basename(urlparse(line).path).replace('.git', '')
        clone_path = os.path.join(cache_dir, repo_name)
        _clone_repo(line, clone_path)
        return clone_path  # Chemin du dépôt cloné
    elif os.path.isdir(line):
        return line
    else:
        loguru.logger.error(f"Invalid path or url: {line}")


def _update_cache(input_file):
    merged_dict = {}
    loguru.logger.info(f"Updating cache with urls and paths from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as yaml_stream:
        urls = yaml.load(yaml_stream, Loader=yaml.FullLoader)
        for u in urls["urls"]:
            loguru.logger.debug(u)
            resource_path = _handle_line(u, get_cache_ew_dir())
            loguru.logger.debug(f"Resource path: {resource_path}")
            if resource_path and os.path.isdir(resource_path):
                for root, dirs, files in os.walk(resource_path):
                    for file in files:
                        if file.endswith('.yaml') and not file.startswith('.'):
                            _process_yaml_file(os.path.join(root, file), merged_dict)
            elif resource_path and os.path.isfile(resource_path):
                _process_yaml_file(resource_path, merged_dict)

    with open(get_cache_ew_cache_file(), 'w') as file:
        yaml.dump(merged_dict, file)
    return merged_dict


def list_command(args):
    table = Table(title="Binary List" + (" (Global)" if args["global"] else " (Local)"))

    if args["global"] and (args["force_update"] or not os.path.exists(get_cache_ew_cache_file())):
        loguru.logger.info("Update and list binaries available globally.")
        result = _update_cache(get_cache_ew_config_file())
        table.add_column("ID", justify="right")
        table.add_column("Name", justify="right")
        table.add_column("Versions", justify="right")
        table.add_column("Alias", justify="right")
    elif args["global"] and os.path.exists(get_cache_ew_cache_file()):
        loguru.logger.info("List binaries available globally using cache.")
        result = yaml.safe_load(open(get_cache_ew_cache_file(), 'r'))
        table.add_column("ID", justify="right")
        table.add_column("Name", justify="right")
        table.add_column("Versions", justify="right")
        table.add_column("Alias", justify="right")
    else:
        table.add_column("Path", justify="right")
        table.add_column("ID", justify="right")
        table.add_column("Versions", justify="right")
        table.add_column("Alias", justify="right")
        result = {}
        loguru.logger.info(f"List binaries available locally.")
        for d in os.listdir(os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE)):
            if os.path.isdir(os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE, d)):
                result[d] = {"id": os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE, d),
                             "versions": [{"version": os.path.basename(d).split(".")[-1], "alias": []}]}

    for k, v in result.items():
        for vv in v["versions"]:
            table.add_row(str(v["id"]), k, vv["version"], ",".join(vv["alias"]))
    console = Console()
    console.print(table)


def add(args):
    loguru.logger.info(f"Add binary with id {args['name']} and version {args['ew_version']}")
    with open(get_cache_ew_cache_file(), 'r') as f:
        result = yaml.safe_load(f)
        solver_configuration = [v for k, v in result.items() if v["id"] == args["name"]]
        if len(solver_configuration) == 0:
            loguru.logger.error(f"Binary with id {args['name']} not found.")
            return
        if len(solver_configuration) > 1:
            loguru.logger.error(f"Binary with id {args['name']} is not unique.")
            return
        solver_configuration = solver_configuration[0]
        version = args["ew_version"]
        try:
            solver_id = ".".join([solver_configuration["id"], version])
            solver_path = os.path.join(args.get("campaign_dir"), METRICS_DIR_EXPERIMENT_WARE, solver_id)
            os.makedirs(solver_path, exist_ok=False)

            cloned_repo = Repo.clone_from(solver_configuration["git"],
                                          solver_path)
            version_configuration = [v for v in solver_configuration["versions"] if
                                     v["version"] == version or version in v["alias"]]
            if len(version_configuration) == 0:
                loguru.logger.error(
                    f"Version {version} not found for binary with id {solver_configuration['id']}.")
                sys.exit(1)
            if len(version_configuration) > 1:
                loguru.logger.error(
                    f"Version {version} is not unique for binary with id {solver_configuration['id']}.")
                sys.exit(1)
            version_configuration = version_configuration[0]
            cloned_repo.git.checkout(version_configuration["git_tag"])
            loguru.logger.info(
                f"Binary with id {solver_configuration['id']} and version {version} added to campaign.")
            loguru.logger.info(f"Path: {solver_path}")
            loguru.logger.info(f"Use `metrics binary build {solver_id}` to build the binary.")

            if not os.path.exists(os.path.join(solver_path, BUILD_SH) and "build_command" in solver_configuration and
                                  solver_configuration["build_command"] is not None):
                with open(os.path.join(solver_path, BUILD_SH), 'w') as f:
                    f.write("#!/bin/bash\n")
                    f.write(f'{solver_configuration["build_command"]}\n')
            if not os.path.exists(os.path.join(solver_path, EXEC_SH)):
                template_builder = BinaryBuilder(solver_path)
                template_builder.add_executable(version_configuration["executable"])
                template_builder.add_command_prefix(solver_configuration.get("command_prefix"))
                template_builder.add_parameters(solver_configuration["command_line"],
                                                solver_configuration.get("always_include_options"))
                template_builder.build("exec.template.sh", EXEC_SH)
            if not os.path.exists(os.path.join(solver_path, BEFORE_SH)):
                template_builder = BinaryBuilder(solver_path)
                template_builder.build("before.template.sh", BEFORE_SH)
            if not os.path.exists(os.path.join(solver_path, AFTER_SH)):
                template_builder = BinaryBuilder(solver_path)
                template_builder.build("after.template.sh", AFTER_SH)
        except FileExistsError:
            loguru.logger.error(
                f"Path for binary with id {solver_configuration['id']} and version {version} already "
                f"exists ({solver_path}).")
            sys.exit(1)


def build(args):
    solver_id = args.get("id")
    campaign_dir = args.get("campaign_dir")
    solver_path = os.path.join(campaign_dir, METRICS_DIR_EXPERIMENT_WARE, solver_id)
    with ChangeDirectory(solver_path):
        if not os.path.exists(BUILD_SH):
            loguru.logger.error(f"File {BUILD_SH} not found in {solver_path}.")
            sys.exit(1)
        if not os.access(BUILD_SH, os.X_OK):
            loguru.logger.error(f"File {BUILD_SH} is not executable.")
            loguru.logger.info("We try to change the permission.")
            st = os.stat(BUILD_SH)
            os.chmod(BUILD_SH, st.st_mode | stat.S_IEXEC)
            if not os.access(BUILD_SH, os.X_OK):
                loguru.logger.error(f"Change permission failed.")
                sys.exit(1)
        loguru.logger.info("Build binary.")
        p = subprocess.Popen(["./build.sh"], stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        loguru.logger.info("Build output (stdout): ")
        loguru.logger.info(out.decode("utf-8"))
        loguru.logger.info("Build output (stderr): ")
        loguru.logger.error(err.decode("utf-8"))


def repo(args):
    with open(get_cache_ew_config_file(), 'r', encoding='utf-8') as yaml_stream:
        urls = yaml.load(yaml_stream, Loader=yaml.FullLoader)
        if 'url' in args and args['url'] is not None:
            loguru.logger.info(f"Adding a new source for experiment_ware:  {args['url']}")
            urls["urls"].append(args['url'])
            with open(get_cache_ew_config_file(), 'w') as file:
                yaml.dump(urls, file)
            show_source_ew(urls)
        elif 'remove' in args and args['remove'] is not None:
            loguru.logger.info(f"Removing source for experiment_ware with id: {args['remove']}")
            urls["urls"].pop(args['remove'] - 1)
            with open(get_cache_ew_config_file(), 'w') as file:
                yaml.dump(urls, file)
            show_source_ew(urls)
        else:
            show_source_ew(urls)


def show_source_ew(urls):
    table = Table(title="List of source of binaries")
    table.add_column("Path or URL", justify="right")
    for u in urls["urls"]:
        table.add_row(u)
    console = Console()
    console.print(table)


MAP_COMMAND = {
    "list": list_command,
    "add": add,
    "build": build,
    "repo": repo
}


def manage_command(args):
    """
    Manage the command for the binary subcommand.
    """
    subcommand = args['subcommand']
    MAP_COMMAND.get(subcommand, unknown_command)(args)
