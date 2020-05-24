import calendar
import json
import os
import re
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

from metrics.core.builder.builder import CampaignBuilder, AttributeManagerSets


class TripodReader:
    def __init__(self, root_path: str, name: str, memout: int, timeout: int):
        self._root_path = root_path
        self._memout = memout
        self._timeout = timeout
        self._name = name
        self._configuration = set()
        with open(f'{root_path}/timeout.output') as f:
            self._timeout_configuration = f.readlines()
            self._timeout_configuration = list(
                map(lambda x: x.replace('\n', '').replace('./', ''), self._timeout_configuration))
        with open(f'{root_path}/empty.output') as f:
            self._empty_configuration = f.readlines()
            self._empty_configuration = list(
                map(lambda x: x.replace('\n', '').replace('./', ''), self._empty_configuration))
        with open(f'{root_path}/r2.output') as f:
            self._valid_configuration = f.readlines()
            self._valid_configuration = list(
                map(lambda x: x.replace('\n', '').replace('./', ''), self._valid_configuration))

        self.campaign = self._make_campaign()

    @staticmethod
    def _loads_stats_json(path_stats):
        with open(path_stats, 'r') as f:
            line = f.readline().replace('"', '').replace("'", '"').replace('True', 'true').replace('False',
                                                                                                   'false').replace(
                'None',
                'null')
            return json.loads(line)

    @staticmethod
    def _generate_configuration_name(data):
        return '_'.join(list(map(str, data['general_configuration'].values()))) + '_'.join(
            list(map(str, data['time_series_configuration'].values()))) + '_'.join(
            list(map(str, data['regression_model_configuration'].values())))

    def _make_campaign(self):
        cb = self.cb = CampaignBuilder(AttributeManagerSets())
        cb['name'] = self._name
        cb['timeout'] = float(self._timeout)
        cb['memout'] = float(self._memout)
        cb['date'] = datetime.now()

        print("Load configuration....")

        self._find_configuration()
        base = '2018-11-15'
        dates = [datetime.strptime(base, '%Y-%m-%d') + relativedelta(months=i) for i in range(12)]
        print("Create Experiment ware....")
        for xpware in tqdm(self._configuration):
            self._create_experiment_ware(xpware)

        self._create_inputset({'name': 'ADP', 'input': [
            self._generate_instance_name(d) for d in dates]})

        self._create_experiments()

        return cb.build()

    @staticmethod
    def _generate_instance_name(d):
        return f'train_{d.strftime("%Y-%m-%d")}_test_{(d + relativedelta(months=2)).strftime("%B")}'

    def _find_configuration(self):
        for d in tqdm(os.listdir(self._root_path)):
            if d not in self._valid_configuration or not os.path.isdir(
                    f'{self._root_path}/{d}' or d in self._timeout_configuration):
                continue
            d2 = list(filter(lambda x: x.startswith('2019'), os.listdir(f'{self._root_path}/{d}')))
            if len(d2) == 0:
                continue

            path_stats = f'{self._root_path}/{d}/{d2[0]}/stats.json'
            if os.path.isfile(path_stats):
                line = TripodReader._loads_stats_json(path_stats)
                data = json.loads(line)
                configuration = TripodReader._generate_configuration_name(data)
                self._configuration.add(configuration)

    def _create_experiment_ware(self, obj):
        ewb = self.cb.add_experiment_ware_builder()
        ewb['name'] = obj
        ewb['date'] = datetime.now()

    def _create_inputset(self, set):
        esb = self.esb = self.cb.add_input_set_builder()
        esb['name'] = set['name']
        for input in set['instances']:
            self._create_input(input)

    def _create_input(self, input):
        ib = self.esb.add_input_builder()
        ib['input'] = input

    def _create_experiments(self):
        for d in tqdm(os.listdir(self._root_path)):
            if d not in self._valid_configuration or not os.path.isdir(
                    f'{self._root_path}/{d}' or d in self._timeout_configuration):
                continue
            d2 = list(filter(lambda x: x.startswith('2019'), os.listdir(f'{self._root_path}/{d}')))
            if len(d2) == 0:
                continue

            path_stats = f'{self._root_path}/{d}/{d2[0]}/stats.json'
            runsolver_stat = f'{self._root_path}/{d}/statistics.out'
            forecast = f'{self._root_path}/{d}/{d2[0]}/forecasts.csv'
            regression_tripod_groupby = f'{self._root_path}/{d}/{d2[0]}/regression_tripod_groupby.csv'
            regression_tripod_no_groupby = f'{self._root_path}/{d}/{d2[0]}/regression_tripod_no_groupby.csv'

            stats = self._loads_stats_json(path_stats)
            date = datetime.strptime(stats['name'][:10], '%Y-%m-%d')
            month_test = (date + relativedelta(month=2)).strftime('%m')
            year_test = (date + relativedelta(month=2)).strftime('%Y')

            eb = self.cb.add_experiment_builder()
            eb['experiment_ware'] = TripodReader._generate_configuration_name(stats)
            eb['input'] = TripodReader._generate_instance_name(date)
            memory, cpu_time = TripodReader._get_run_solver_information(runsolver_stat)
            eb['memory'] = memory
            eb['cpu_time'] = cpu_time

            df = pd.DataFrame()

            df['y_test'] = stats['y_test']
            df['date_test'] = sorted(stats['date_test'])

            regression_result = pd.read_csv(regression_tripod_no_groupby)
            regression_result['date_test'] = stats['date_test']

            last_day_of_month = calendar.monthrange(int(year_test), int(month_test))[1]

            min_date = f'{int(year_test)}-{int(month_test)}-01'
            max_date = f'{int(year_test)}-{int(month_test)}-{last_day_of_month}'

            eb['y_test'] = cpu_time

    @staticmethod
    def _get_run_solver_information(file):
        regex = (r"CPUTIME=(?P<cputime>\d+.\d+)\n"
                 r"# .*\n"
                 r"USERTIME=(?P<usertime>\d+.\d+)\n"
                 r"# .*\n"
                 r"SYSTEMTIME=(?P<systemtime>\d+.\d+)\n"
                 r"# .*\n"
                 r"CPUUSAGE=(?P<cpuusage>\d+.\d+)\n"
                 r"# .*\n"
                 r"MAXVM=(?P<memory>\d+.\d*)")

        with open(file, 'r') as f:
            string = f.read()
            result = re.search(regex, string, flags=re.MULTILINE)
            return result.group('memory'), result.group('cputime')
