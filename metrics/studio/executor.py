import os
import subprocess

from metrics.studio.constant import METRICS_DIR_EXPERIMENT_WARE


class ShellWrapper:
    def __init__(self, script_to_launch, root_dir='.'):
        self.script_to_launch = os.path.join(root_dir, METRICS_DIR_EXPERIMENT_WARE, script_to_launch)
        self._options = []

    def add_option(self, option):
        self._options.append(option)

    def run(self):
        with subprocess.Popen([self.script_to_launch] + self._options, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as p:
            stdout, stderr = p.communicate()


class StartShell(ShellWrapper):
    def __init__(self, script_to_launch, root_dir='.'):
        super().__init__("start.sh", root_dir=root_dir)

    def add_campaign_dir(self, campaign_dir):
        self.add_option(campaign_dir)

    def add_instance(self, instance):
        self.add_option(instance)

    def add_solver_name(self, solver_name):
        self.add_option(solver_name)

    def add_solver_version(self, solver_version):
        self.add_option(solver_version)

    def add_solver_dir(self, solver_dir):
        self.add_option(solver_dir)


class RunSolverShell(StartShell):
    def __init__(self, script_to_launch, root_dir='.'):
        super().__init__("runsolverw.sh", root_dir=root_dir)

    def add_cpu_time(self, cpu_time):
        self.add_option(str(cpu_time))

    def add_wall_time(self, wall_time):
        self.add_option(str(wall_time))

    def add_memout(self, memout):
        self.add_option(str(memout))

    def add_delay(self, delay):
        self.add_option(str(delay))

    def add_output_directory(self, output_directory):
        self.add_option(output_directory)
