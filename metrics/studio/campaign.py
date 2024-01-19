import os.path
from typing import Any

import loguru
import yaml
from jinja2 import Environment, PackageLoader, select_autoescape

from metrics.studio.util import convert_to_seconds


class Campaign:
    # campaign_directory, host, port, cpu, wall, memout, delay, qos, parition, nNodes, nCpu,
    def __init__(self, root_dir='.'):
        self._env = Environment(loader=PackageLoader('metrics'), autoescape=select_autoescape())
        self._root_dir = root_dir
        self._template_vars = {'slurm': {}, 'runsolver': {},'hpc':{}}

    def _write_template(self, template_name: str, output_file: str) -> None:
        """
        Writes a report file following a template.

        :param template_name: The name of the file to use as template.
        :param output_file: The path of the output file (relative to the root directory of
                            the report).
        """
        with open(os.path.join(self._root_dir, output_file), 'w') as file:
            template = self._env.get_template(template_name)
            all_vars = self._template_vars["hpc"]
            all_vars.update(self._template_vars["slurm"])
            all_vars.update(self._template_vars["runsolver"])
            print(template.render(**all_vars), file=file)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets the value of an item that should be rendered in a template.

        :param key: The name of the value to set.
        :param value: The value to set.
        """
        self._template_vars[key] = value

    def __getitem__(self, item: str) -> Any:
        """
        Gives the value of an item that should be rendered in a template.

        :param item: The name of the value to get.

        :return: The value associated with the given name.
        """
        return self._template_vars[item]

    def save(self):
        self._write_template('.campaign.yml','.campaign.yml')


def campaigns_init(arguments, cb: 'CampaignBuilder'):
    if arguments["campaign_directory"]:
        cb.add_campaign_directory(arguments["campaign_directory"])
    if arguments["host"]:
        cb.add_host(arguments["host"])
    if arguments["port"]:
        cb.add_host(arguments["ports"])
    if arguments["qos"]:
        cb.add_qos(arguments["qos"])
    if arguments["partition"]:
        cb.add_partition(arguments["partition"])
    if arguments["n_nodes"]:
        cb.add_nNodes(arguments["n_nodes"])
    if arguments["n_cpu"]:
        cb.add_partition(arguments["n_cpu"])
    if arguments["cpu"]:
        cb.add_cpu_timeout(arguments["cpu"])
    if arguments["wall"]:
        cb.add_wall_timeout(arguments["wall"])
    if arguments["delay"]:
        cb.add_delay(arguments["delay"])
    if arguments["memout"]:
        cb.add_memout(arguments["memout"])
    return cb


class CampaignFactory:
    @staticmethod
    def campaign_builder(arguments, file) -> 'CampaignBuilder':
        campaign_file = ".campaign.yml"
        cb = CampaignBuilder()
        if os.path.exists(campaign_file):
            with open(campaign_file, "r") as stream:
                try:
                    data = yaml.safe_load(stream)
                    loguru.logger.debug(data)

                except yaml.YAMLError as exc:
                    loguru.logger.error("Failed to parse the '.campaign.yml' file.")
        loguru.logger.debug(arguments)
        if arguments["subcommand"] == "init":
            cb = campaigns_init(arguments, cb)
        return cb


class CampaignBuilder:
    def __init__(self, root_dir='.'):
        self._campaign = Campaign(root_dir=root_dir)
        # self._name = None
        # self._campaign_directory = None
        # self._host = None
        # self._port = 22
        # self._cpu_timeout = None
        # self._wall_timeout = None
        # self._memout = None
        # self._delay = None
        # self._qos = None
        # self._partition = None
        # self._nNodes = None
        # self._nCpu = None

    def add_host(self, host):
        self._campaign["hpc"]["host"] = host

    def add_port(self, port):
        self._campaign["hpc"]["port"] = port

    def add_campaign_directory(self, cp):
        self._campaign["hpc"]["campaign_directory"] = cp

    def add_cpu_timeout(self, timeout):
        self._campaign["runsolver"]["cpu_timeout"] = convert_to_seconds(timeout)

    def add_wall_timeout(self, timeout):
        self._campaign["slurm"]["wall_timeout"] = convert_to_seconds(timeout)

    def add_memout(self, memout):
        self._campaign["runsolver"]["memory_out"] = memout

    def add_delay(self, delay):
        self._campaign["runsolver"]["delay"] = convert_to_seconds(delay)

    def add_qos(self, qos):
        self._campaign["slurm"]["qos"] = qos

    def add_partition(self, partition):
        self._campaign["slurm"]["partition"] = partition

    def add_nNodes(self, nNodes):
        self._campaign["slurm"]["n_nodes"] = nNodes

    def add_nCpu(self, nCpu):
        self._campaign["slurm"]["n_cpu"] = nCpu

    def build(self) -> Campaign:
        return self._campaign
