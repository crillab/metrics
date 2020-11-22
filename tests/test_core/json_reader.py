
import json
import re
from datetime import datetime

from metrics.core.builder.builder import CampaignBuilder
from metrics.core.constants import *


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
        cb[CAMPAIGN_NAME] = self.obj['name']
        cb[CAMPAIGN_TIMEOUT] = float(self.obj['timeout'])
        cb[CAMPAIGN_MEMOUT] = float(self.obj['memout'])
        cb['date'] = datetime.now()

        for xpware in self.obj['configurations']:
            self._create_experiment_ware(xpware)

        self._create_inputset(self.obj['instance_set_id'])

        for xp in self.obj['experimentations']:
            self._create_experiment(xp)

        return cb.build()

    def _create_experiment_ware(self, obj):
        ewb = self.cb.add_experiment_ware_builder()
        ewb[XP_WARE_NAME] = obj['name']
        ewb['date'] = datetime.now()

    def _create_experiment(self, xp):
        eb = self.cb.add_experiment_builder()
        eb[EXPERIMENT_INPUT] = xp['instance']
        eb['start_time'] = datetime.strptime(xp['date'], '%Y-%m-%d')
        eb[EXPERIMENT_XP_WARE] = xp['configuration']
        eb['status'] = xp['Global_Stop']
        eb[EXPERIMENT_CPU_TIME] = xp['Global_cpu'] if xp['Global_Stop'] not in {'TODO', 'EXCEEDED_TIME'} else 3600.

        if 'arm_res' in xp:
            eb['arm_res'] = xp['arm_res']

    def _create_inputset(self, set):
        esb = self.esb = self.cb.add_input_set_builder()
        esb[INPUT_SET_NAME] = set['name']
        for input in set['instances']:
            self._create_input(input)

    def _create_input(self, input):
        ib = self.esb.add_input_builder()
        ib[INPUT_NAME] = input['path']
        ib['Constraints_arities'] = input['Constraints_arities']
        ib['Constraints_distribution'] = input['Constraints_distribution']
        ib['Variables_degrees'] = input['Variables_degrees']
        ib['family'] = re.search('XCSP.*?/(.+?)/', input['path'], flags=re.IGNORECASE).group(1)