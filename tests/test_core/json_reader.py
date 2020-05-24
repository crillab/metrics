
import json
import re
from datetime import datetime

from metrics.core.builder.builder import AttributeManagerSets, CampaignBuilder


class JsonReader:

    def __init__(self, path: str):
        self.obj = self.read_json(path)
        self.campaign = self._make_campaign()

    def read_json(self, path):
        with open(path) as f:
            data = json.load(f)
        return data

    def _make_campaign(self):
        cb = self.cb = CampaignBuilder()
        cb['name'] = self.obj['name']
        cb['timeout'] = float(self.obj['timeout'])
        cb['memout'] = float(self.obj['memout'])
        cb['date'] = datetime.now()

        for xpware in self.obj['configurations']:
            self._create_experiment_ware(xpware)

        self._create_inputset(self.obj['instance_set_id'])

        for xp in self.obj['experimentations']:
            self._create_experiment(xp)

        return cb.build()

    def _create_experiment_ware(self, obj):
        ewb = self.cb.add_experiment_ware_builder()
        ewb['name'] = obj['name']
        ewb['date'] = datetime.now()

    def _create_experiment(self, xp):
        eb = self.cb.add_experiment_builder()
        eb['input'] = xp['instance']
        eb['start_time'] = datetime.strptime(xp['date'], '%Y-%m-%d')
        eb['experiment_ware'] = xp['configuration']
        eb['cpu_time'] = xp['Global_cpu'] if xp['Global_Stop'] not in {'TODO', 'EXCEEDED_TIME'} else 3600.

        if 'arm_res' in xp:
            eb['arm_res'] = xp['arm_res']

    def _create_inputset(self, set):
        esb = self.esb = self.cb.add_input_set_builder()
        esb['name'] = set['name']
        for input in set['instances']:
            self._create_input(input)

    def _create_input(self, input):
        ib = self.esb.add_input_builder()
        ib['path'] = input['path']
        ib['family'] = re.search('XCSP.*?/(.+?)/', input['path'], flags=re.IGNORECASE).group(1)