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


class Campaign:
    # campaign_directory, host, port, cpu, wall, memout, delay, qos, parition, nNodes, nCpu,
    def __init__(self, root_dir='.', config: Dict[str, Any] = None):
        self._root_dir = root_dir
        self._config = config

    @property
    def campaign_dir(self):
        return self._config['ssh'].get('campaign_directory')

    @property
    def ssh_hostname(self):
        return self._config['ssh']['host']

    @property
    def cpu_time(self):
        return self._config['setup']['timeout']

    @property
    def wall_time(self):
        return self._config['setup']['wall_timeout']

    @property
    def memout(self):
        return self._config['setup']['memout']

    @property
    def delay(self):
        return self._config['setup']['delay']

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
            return Campaign(os.getcwd(), self._template_vars)

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
            shutil.copytree(source_scripts, os.path.join(self._root_dir, METRICS_DIR_EXPERIMENT_WARE),
                            dirs_exist_ok=True)
        except Exception as e:
            loguru.logger.error(f"Error copying the directory {source_scripts} to {METRICS_DIR_EXPERIMENT_WARE}")
            loguru.logger.error(e)

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
                                     local_directory=os.path.abspath(self._root_dir),
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
