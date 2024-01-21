import os.path
from typing import Any

import loguru
import yaml
from jinja2 import Environment, PackageLoader, select_autoescape
from peewee import Model, CharField, SqliteDatabase

from metrics.studio.util import convert_to_seconds, get_cache_dir

db = SqliteDatabase(os.path.join(get_cache_dir(), "campaign.db"))


class CampaignModel(Model):
    name = CharField(max_length=1024)
    local_directory = CharField(unique=True, max_length=2048)

    class Meta:
        database = db  # This model uses the "people.db" database.


db.connect(reuse_if_open=True)
db.create_tables([CampaignModel], safe=True)


class Campaign:
    # campaign_directory, host, port, cpu, wall, memout, delay, qos, parition, nNodes, nCpu,
    def __init__(self, root_dir='.'):
        self._env = Environment(loader=PackageLoader('metrics'), autoescape=select_autoescape())
        self._root_dir = root_dir
        self._template_vars = {'slurm': {}, 'runsolver': {}, 'ssh': {}}

    @property
    def campaign_dir(self):
        return self._template_vars['slurm']['campaign_dir']

    @property
    def ssh_hostname(self):
        return self._template_vars['slurm']['hostname']

    def _write_template(self, template_name: str, output_file: str) -> None:
        """
        Writes a report file following a template.

        :param template_name: The name of the file to use as template.
        :param output_file: The path of the output file (relative to the root directory of
                            the report).
        """
        with open(os.path.join(self._root_dir, output_file), 'w') as file:
            template = self._env.get_template(template_name)
            all_vars = self._template_vars["ssh"]
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

    def update_dict(self, yaml_data):
        self._template_vars.update(yaml_data)

    def save(self):
        self._write_template('.campaign.yml', '.campaign.yml')


def campaigns_init_from_argument(arguments, cb: 'CampaignBuilder'):
    if "campaign_directory" in arguments and arguments["campaign_directory"]:
        cb.add_campaign_directory(arguments["campaign_directory"])
    if "host" in arguments and arguments["host"]:
        cb.add_host(arguments["host"])
    if "port" in arguments and arguments["port"]:
        cb.add_port(arguments["port"])
    if "qos" in arguments and arguments["qos"]:
        cb.add_qos(arguments["qos"])
    if "partition" in arguments and arguments["partition"]:
        cb.add_partition(arguments["partition"])
    if "n_nodes" in arguments and arguments["n_nodes"]:
        cb.add_n_nodes(arguments["n_nodes"])
    if "n_cpu" in arguments and arguments["n_cpu"]:
        cb.add_partition(arguments["n_cpu"])
    if "cpu" in arguments and arguments["cpu"]:
        cb.add_cpu_timeout(arguments["cpu"])
    if "wall" in arguments and arguments["wall"]:
        cb.add_wall_timeout(arguments["wall"])
    if "delay" in arguments and arguments["delay"]:
        cb.add_delay(arguments["delay"])
    if "memout" in arguments and arguments["memout"]:
        cb.add_memout(arguments["memout"])
    return cb


def campaigns_init_from_dict(yaml_data, cb: 'CampaignBuilder'):
    cb.add_data_from_dict(yaml_data)
    return cb


class CampaignFactory:
    @staticmethod
    def campaign_builder(arguments, file) -> 'CampaignBuilder':
        cb = CampaignBuilder()
        if os.path.exists(file):
            with open(file, "r") as stream:
                try:
                    data = yaml.safe_load(stream)
                    loguru.logger.debug(data)
                    campaigns_init_from_dict(data, cb)
                except yaml.YAMLError as exc:
                    loguru.logger.error(f"Failed to parse the '.campaign.yml' file. {exc}")
        loguru.logger.debug(arguments)
        cb = campaigns_init_from_argument(arguments, cb)
        return cb


class CampaignBuilder:
    def __init__(self, root_dir='.'):
        self._campaign = Campaign(root_dir=root_dir)

    def add_host(self, host):
        self._campaign["ssh"]["host"] = host

    def add_port(self, port):
        self._campaign["ssh"]["port"] = port

    def add_campaign_directory(self, cp):
        self._campaign["ssh"]["campaign_directory"] = cp

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

    def add_n_nodes(self, nNodes):
        self._campaign["slurm"]["n_nodes"] = nNodes

    def add_n_cpu(self, nCpu):
        self._campaign["slurm"]["n_cpu"] = nCpu

    def add_data_from_dict(self, d):
        self._campaign.update_dict(d)

    def build(self) -> Campaign:
        return self._campaign
