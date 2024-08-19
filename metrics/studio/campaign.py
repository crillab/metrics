import os.path
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict

import loguru
import peewee
import yaml
from peewee import Model, CharField, DateTimeField

from metrics.studio.common import TemplateBuilder
from metrics.studio.constant import METRICS_DIR_CONFIG, METRICS_DIR_EXPERIMENT_WARE, METRICS_TEMPLATE_PATH
from metrics.studio.database import db


class CampaignModel(Model):
    name = CharField(max_length=1024)
    local_directory = CharField(unique=True, max_length=2048)
    remote_directory = CharField(unique=True, max_length=2048, null=True, default=None)
    status = CharField(max_length=256, null=True)
    date = DateTimeField(default=datetime.now())

    def __str__(self):
        return f"{self.name}"

    class Meta:
        database = db


# class Campaign:
#     # campaign_directory, host, port, cpu, wall, memout, delay, qos, parition, nNodes, nCpu,
#     def __init__(self, root_dir='.'):
#         self._env = Environment(loader=PackageLoader('metrics'), autoescape=select_autoescape())
#         self._root_dir = root_dir
#         self._template_vars = {'slurm': {}, 'runsolver': {}, 'ssh': {}}
#
#     @property
#     def campaign_dir(self):
#         return self._template_vars['ssh'].get('campaign_directory')
#
#     @property
#     def ssh_hostname(self):
#         return self._template_vars['ssh']['host']
#
#     def _write_template(self, template_name: str, output_file: str) -> None:
#         """
#         Writes a report file following a template.
#
#         :param template_name: The name of the file to use as template.
#         :param output_file: The path of the output file (relative to the root directory of
#                             the report).
#         """
#         with open(os.path.join(self._root_dir, output_file), 'w') as file:
#             template = self._env.get_template(template_name)
#             all_vars = self._template_vars["ssh"]
#             all_vars.update(self._template_vars["slurm"])
#             all_vars.update(self._template_vars["runsolver"])
#             print(template.render(**all_vars), file=file)
#
#     def __setitem__(self, key: str, value: Any) -> None:
#         """
#         Sets the value of an item that should be rendered in a template.
#
#         :param key: The name of the value to set.
#         :param value: The value to set.
#         """
#         self._template_vars[key] = value
#
#     def __getitem__(self, item: str) -> Any:
#         """
#         Gives the value of an item that should be rendered in a template.
#
#         :param item: The name of the value to get.
#
#         :return: The value associated with the given name.
#         """
#         return self._template_vars[item]
#
#     def update_dict(self, yaml_data):
#         self._template_vars.update(yaml_data)
#
#     def save(self):
#         self._write_template('campaign.yml', 'campaign.yml')
#
#
# def campaigns_init_from_argument(arguments, cb: 'CampaignConfigBuilder'):
#     if "campaign_directory" in arguments and arguments["campaign_directory"]:
#         cb.add_campaign_directory(arguments["campaign_directory"])
#     if "host" in arguments and arguments["host"]:
#         cb.add_host(arguments["host"])
#     if "port" in arguments and arguments["port"]:
#         cb.add_port(arguments["port"])
#     if "qos" in arguments and arguments["qos"]:
#         cb.add_qos(arguments["qos"])
#     if "partition" in arguments and arguments["partition"]:
#         cb.add_partition(arguments["partition"])
#     if "n_nodes" in arguments and arguments["n_nodes"]:
#         cb.add_n_nodes(arguments["n_nodes"])
#     if "n_cpu" in arguments and arguments["n_cpu"]:
#         cb.add_partition(arguments["n_cpu"])
#     if "cpu" in arguments and arguments["cpu"]:
#         cb.add_cpu_timeout(arguments["cpu"])
#     if "wall" in arguments and arguments["wall"]:
#         cb.add_wall_timeout(arguments["wall"])
#     if "delay" in arguments and arguments["delay"]:
#         cb.add_delay(arguments["delay"])
#     if "memout" in arguments and arguments["memout"]:
#         cb.add_memout(arguments["memout"])
#     return cb
#
#
# def campaigns_init_from_dict(yaml_data, cb: 'CampaignConfigBuilder'):
#     print(yaml_data)
#     cb.add_data_from_dict(yaml_data)
#     return cb
#
#
# class CampaignFactory:
#     @staticmethod
#     def campaign_builder(arguments, file) -> 'CampaignConfigBuilder':
#         cb = CampaignConfigBuilder()
#         if os.path.exists(file):
#             with open(file, "r") as stream:
#                 try:
#                     data = yaml.safe_load(stream)
#                     loguru.logger.debug(data)
#                     campaigns_init_from_dict(data, cb)
#                 except yaml.YAMLError as exc:
#                     loguru.logger.error(f"Failed to parse the 'campaign.yml' file. {exc}")
#         loguru.logger.debug(arguments)
#         cb = campaigns_init_from_argument(arguments, cb)
#         return cb


# class CampaignConfigBuilder(AbstractCampaignBuilder):
#     def __init__(self, root_dir=os.getcwd()):
#         super().__init__(root_dir)
#
#
#
#     def update_vars(self, dict: Dict[str, Any]) -> None:
#         """
#         Updates the values of the internal directory with another directory.
#
#         :param dict: The items to update and their new values.
#         """
#         self._template_vars.update(dict)
#
#
#
#
#     # def add_host(self, host):
#     #     self._campaign["ssh"]["host"] = host
#     #
#     # def add_port(self, port):
#     #     self._campaign["ssh"]["port"] = port
#     #
#     # def add_campaign_directory(self, cp):
#     #     self._campaign["ssh"]["campaign_directory"] = cp
#     #
#     # def add_cpu_timeout(self, timeout):
#     #     self._campaign["runsolver"]["cpu_timeout"] = convert_to_seconds(timeout)
#     #
#     # def add_wall_timeout(self, timeout):
#     #     self._campaign["slurm"]["wall_timeout"] = convert_to_seconds(timeout)
#     #
#     # def add_memout(self, memout):
#     #     self._campaign["runsolver"]["memory_out"] = memout
#     #
#     # def add_delay(self, delay):
#     #     self._campaign["runsolver"]["delay"] = convert_to_seconds(delay)
#     #
#     # def add_qos(self, qos):
#     #     self._campaign["slurm"]["qos"] = qos
#     #
#     # def add_partition(self, partition):
#     #     self._campaign["slurm"]["partition"] = partition
#     #
#     # def add_n_nodes(self, nNodes):
#     #     self._campaign["slurm"]["n_nodes"] = nNodes
#     #
#     # def add_n_cpu(self, nCpu):
#     #     self._campaign["slurm"]["n_cpu"] = nCpu
#     #
#     # def add_data_from_dict(self, d):
#     #     self._campaign.update_dict(d)
#     #
#     # def build(self) -> Campaign:
#     #     return self._campaign


class CampaignBuilder(TemplateBuilder):
    """
    The CampaignBuilder provides a convenient interface for creating the different
    files needed to create the environment of the campaign.
    """

    def __init__(self, root_dir: str = '.') -> None:
        """
        Creates a new campaign builder.

        :param root_dir: The directory in which to build the campaign.
        """
        super().__init__(root_dir)

    def load_current_campaign(self):
        campaign_file = os.path.join(self._root_dir, METRICS_DIR_CONFIG, "campaign.yml")
        if not os.path.exists(campaign_file):
            loguru.logger.error("The file 'config/campaign.yml'  does not exist.")
            sys.exit(1)
        with open(campaign_file, 'r', encoding='utf-8') as yaml_stream:
            self._template_vars = yaml.load(yaml_stream)

    def create_directories(self) -> None:
        """
        Creates the directories needed for the campaign.
        """
        loguru.logger.info("Creating directories for the campaign.")
        if not os.path.exists(self._root_dir):
            os.mkdir(self._root_dir)

        for name in ('config', 'experiment_wares', 'experiments', 'input_set'):
            path = os.path.join(self._root_dir, name)
            if not os.path.exists(path):
                os.mkdir(path)
        self._create_environment('venv')

    def _create_environment(self, env_name: str):
        loguru.logger.info("Creating environment")
        # Chemin absolu vers le répertoire de l'environnement virtuel
        env_dir = os.path.join(self._root_dir, env_name)
        self._env_name = env_name

        # Créer l'environnement virtuel
        try:
            subprocess.run([sys.executable, "-m", "venv", env_dir], check=True)
        except subprocess.CalledProcessError as e:
            loguru.logger.error("Error creating virtual environment:", e)
            return

    def install(self) -> None:
        """
        Installs Metrics' dependencies in the current environment.
        """
        loguru.logger.info("Install dependencies...")
        # Déterminer le chemin du binaire pip dans l'environnement virtuel
        if os.name == 'posix':
            pip_command = os.path.join(self._root_dir, self._env_name, "bin", "pip")
        elif os.name == 'nt':
            pip_command = os.path.join(self._root_dir, self._env_name, "Scripts", "pip.exe")
        else:
            loguru.logger.error("Unsupported operating system.")
            return

        # Appeler le binaire pip avec les arguments fournis
        try:
            loguru.logger.info(f"Launching pip command : {pip_command}")
            subprocess.run([pip_command] + ["install", "crillab-metrics", "jupyter"], check=True)
        except subprocess.CalledProcessError as e:
            loguru.logger.error("Error calling pip in the virtual environment:", e)

    def git_init(self) -> None:
        """
        Initializes a git repository inside the campaign directory.
        """
        loguru.logger.info(f"Init git for {self._root_dir}")
        os.system(f'git init "{self._root_dir}"')
        self._write_template('gitignore', '.gitignore')

    def add_readme(self) -> None:
        """
        Adds a README file to the campaign.
        """
        loguru.logger.info(f"Adding readme file. ")
        self._write_template('README.md', 'README.md')

    def add_requirements(self) -> None:
        """
        Adds the requirements file to the campaign (i.e., the file listing all the dependencies
        that should be installed to execute the campaign).
        """
        loguru.logger.info(f"Adding requirements file.")
        self._write_template('requirements.txt', 'requirements.txt')

    def add_campaign_config(self) -> None:
        """
        Adds Campaign's configuration to the campaign.
        """
        self._write_template('campaign.yml', os.path.join('config', 'campaign.yml'))

    def add_scripts(self) -> None:
        """
        Adds the start script to the campaign.
        """
        self._write_template('start.sh', os.path.join(METRICS_DIR_EXPERIMENT_WARE, 'start.sh'))
        source_scripts = os.path.join(METRICS_TEMPLATE_PATH, 'scripts')
        try:
            shutil.copytree(source_scripts, os.path.join(self.root_dir, METRICS_DIR_EXPERIMENT_WARE),
                            dirs_exist_ok=True)
        except Exception as e:
            loguru.logger.error(f"Error copying the directory {source_scripts} to {METRICS_DIR_EXPERIMENT_WARE}", e)

    def add_run_solver(self) -> None:
        bin_dir = os.path.join(self._root_dir, METRICS_DIR_EXPERIMENT_WARE, "bin")
        try:
            if not os.path.exists(bin_dir):
                os.makedirs(bin_dir, exist_ok=True)
            shutil.copyfile(os.path.join(METRICS_TEMPLATE_PATH, "runsolver"), os.path.join(bin_dir, "runsolver"))
        except Exception as e:
            loguru.logger.error(f"Error copying the file runsolver to {bin_dir}", e)

    def register(self):
        """
        Registers the campaign in the local database.
        """
        loguru.logger.info("Registering the campaign in the local database.")

        try:
            m = CampaignModel.create(name=self._template_vars['title'] or self._root_dir,
                                     local_directory=self._root_dir,
                                     remote_directory=None)
            m.save()
        except peewee.PeeweeException as e:
            loguru.logger.error(f"Exception for registering campaign with the path {self._root_dir}", e)

    def shell(self):
        script_path = os.path.join(self._env_name, "Scripts", "activate")
        activate_script = os.path.join(self._root_dir, script_path)
        if not os.path.exists(activate_script):
            script_path = os.path.join(self._env_name, "bin", "activate")
            activate_script = os.path.join(self._root_dir, script_path)
            if not os.path.exists(activate_script):
                loguru.logger.error("Cannot find virtual environment activation script.")
                return

        os.chdir(self._root_dir)

        # Activate the virtual environment in an interactive shell
        if os.name == 'posix':  # If the operating system is UNIX-like
            try:
                subprocess.run(["bash", "-c", f"source {script_path} && exec $SHELL"], check=True)
            except subprocess.CalledProcessError as e:
                loguru.logger.error("Error activating virtual environment:", e)
                loguru.logger.error(f"Working directory:{os.getcwd()}")
                loguru.logger.error(f"You can activate the virtual environment manually by running: {activate_script}")
        elif os.name == 'nt':  # If the operating system is Windows
            try:
                subprocess.run(["cmd", "/K", activate_script], check=True)
            except subprocess.CalledProcessError as e:
                loguru.logger.error("Error activating virtual environment:", e)
        else:
            loguru.logger.error("Unsupported operating system.")

    def update_vars(self, variables: Dict[str, Any]) -> None:
        """
        Updates the values of some items that should be rendered in a template.

        :param variables: The items to update and their new values.
        """
        self._template_vars.update(variables)
