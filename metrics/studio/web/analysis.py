from typing import Callable, Any

from metrics.core.model import Campaign
from metrics.wallet.dataframe.builder import Analysis, CampaignDataFrameBuilder


class AnalysisWeb:

    def __init__(self, campaign: Campaign, is_success: Callable[[Any], bool] = None):
        self._campaign = campaign
        self._is_success = (lambda x: x['cpu_time'] < self._campaign.timeout) if is_success is None else is_success
        self._campaign_df = self._make_campaign_df()

    @property
    def campaign_df(self):
        return self._campaign_df


    def _make_campaign_df(self):
        campaign_df = CampaignDataFrameBuilder(self._campaign).build_from_campaign()
        campaign_df.data_frame['success'] = campaign_df.data_frame.apply(self._is_success, axis=1)
        campaign_df.data_frame['cpu_time'] = campaign_df.data_frame.apply(
            lambda x: x['cpu_time'] if x['success'] else campaign_df.campaign.timeout, axis=1)
        return campaign_df

