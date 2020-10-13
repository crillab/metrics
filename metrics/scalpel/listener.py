###############################################################################
#                                                                             #
#  Scalpel - A Metrics Module                                                 #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                #
#  -------------------------------------------------------------------------- #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  sCAlPEL - extraCting dAta of exPeriments from softwarE Logs                #
#                                                                             #
#                                                                             #
#  This program is free software: you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation, either version 3 of the License, or (at your #
#  option) any later version.                                                 #
#                                                                             #
#  This program is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                       #
#  See the GNU General Public License for more details.                       #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this program.                                                   #
#  If not, see <https://www.gnu.org/licenses/>.                               #
#                                                                             #
###############################################################################


"""
This module provides a listener which listens to the events triggered while
a campaign is being parsed, so as to build its representation.
"""


from collections import defaultdict
from typing import Any, Dict, List, Tuple, Union

from metrics.core.builder import CampaignBuilder
from metrics.core.builder.builder import ModelBuilder
from metrics.core.model import Campaign


class KeyMapping:
    """
    The KeyMapping maps the keys defined in the campaign to parse to that
    expected by Scalpel.
    """

    def __init__(self) -> None:
        """
        Creates a new KeyMapping.
        """
        self._dict_representation = {}

    def __setitem__(self, scalpel_key: str,
                    campaign_key: Union[str, List[str]]) -> None:
        """
        Maps key(s) as defined in the campaign to that expected by Scalpel.

        :param scalpel_key: The key expected by Scalpel.
        :param campaign_key: The key(s) defined in the campaign.
        """
        if isinstance(campaign_key, list):
            self._dict_representation[scalpel_key] = [str(v) for v in campaign_key]
        else:
            self._dict_representation[scalpel_key] = [str(campaign_key)]

    def __getitem__(self, campaign_key: str) -> Tuple[str, int]:
        """
        Gives the key expected by Scalpel that corresponds to the given key.

        :param campaign_key: The key defined in the campaign.

        :return: A tuple having, as first element, the key expected by Scalpel
                 or the given key if no mapping is set for this key and, as
                 second element, the number of values expected for this key.
        """
        for key, value in self._dict_representation.items():
            if campaign_key in value:
                return key, len(value)
        return campaign_key, 1

    def get_sorted_keys(self, scalpel_key: str) -> List[str]:
        """
        Gives the list of the campaign keys that map to the given key expected
        by Scalpel.

        :param scalpel_key: The key expected by Scalpel.

        :return: The list of the campaign keys that map to the given key, in the
                 same order as that specified by the user.
        """
        keys = self._dict_representation.get(scalpel_key)
        if keys is None:
            return [scalpel_key]
        return keys


class CampaignParserListener:
    """
    The CampaignParserListener is a listener notified while parsing a campaign.
    """

    def __init__(self) -> None:
        """
        Creates a new CampaignParserListener.
        """
        self._key_mapping = KeyMapping()
        self._campaign_builder = None
        self._input_set_builder = None
        self._current_builder = None
        self._current_experiment = False
        self._pending_keys = defaultdict(dict)

    def add_key_mapping(self, scalpel_key: str,
                        campaign_key: Union[str, List[str]]) -> None:
        """
        Maps key(s) as defined in the campaign to that expected by Scalpel.

        :param scalpel_key: The key expected by Scalpel.
        :param campaign_key: The key(s) defined in the campaign.
        """
        self._key_mapping[scalpel_key] = campaign_key

    def start_campaign(self) -> None:
        """
        Notifies this listener that a new campaign is going to be parsed.
        """
        self._campaign_builder = CampaignBuilder()
        self._current_builder = self._campaign_builder

    def end_campaign(self) -> None:
        """
        Notifies this listener that the current campaign has been fully parsed.

        :raises ValueError: If some keys are still pending for the current
                            campaign.
        """
        if len(self._pending_keys) > 0:
            raise ValueError('Cannot end current campaign: some values are still pending!')
        self._current_builder = None

    def start_experiment_ware(self) -> None:
        """
        Notifies this listener that a new experiment-ware is going to be parsed.
        """
        self._current_builder = self._campaign_builder.add_experiment_ware_builder()

    def end_experiment_ware(self) -> None:
        """
        Notifies this listener that the current experiment-ware has been
        fully parsed.
        """
        self._current_builder = self._campaign_builder

    def start_input_set(self) -> None:
        """
        Notifies this listener that a new input set is going to be parsed.
        """
        self._input_set_builder = self._campaign_builder.add_input_set_builder()
        self._current_builder = self._input_set_builder

    def end_input_set(self) -> None:
        """
        Notifies this listener that the current input set has been fully parsed.
        """
        self._current_builder = self._campaign_builder
        self._input_set_builder = None

    def start_input(self) -> None:
        """
        Notifies this listener that a new input is going to be parsed.
        """
        self._current_builder = self._input_set_builder.add_input_builder()

    def end_input(self) -> None:
        """
        Notifies this listener that the current input has been fully parsed.
        """
        self._current_builder = self._input_set_builder

    def start_experiment(self) -> None:
        """
        Notifies this listener that a new experiment is going to be parsed.
        """
        self._current_builder = self._campaign_builder.add_experiment_builder()
        self._current_experiment = True

    def end_experiment(self) -> None:
        """
        Notifies this listener that the current experiment has been
        fully parsed.
        """
        self._current_builder = self._campaign_builder
        self._current_experiment = False

    def log_data(self, key: str, value: Any) -> None:
        """
        Notifies this listener about data that has been read.
        This data is set to the element of the campaign that is currently
        being built.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        # If the value is a tuple, its elements are recursively logged.
        if isinstance(value, tuple):
            for v in value:
                self.log_data(key, v)
            return

        # Otherwise, we need to retrieve the mapping for the logged element.
        scalpel_key, nb = self._key_mapping[key]
        read_values = self._pending_keys[scalpel_key]
        read_values[key] = str(value)

        # If all the values of the mapping have been read, we can commit them.
        if len(read_values) == nb:
            values = ['' if read_values[v] is None else read_values[v]
                      for v in self._key_mapping.get_sorted_keys(scalpel_key)]
            identifier = ' '.join(values)
            self._create_if_missing(scalpel_key, identifier, read_values)
            self._current_builder[scalpel_key] = identifier
            del self._pending_keys[scalpel_key]

    def _create_if_missing(self, key: str, identifier: str, all_values: Dict[str, str]) -> None:
        """
        Creates an element of the campaign if it has not been declared yet.

        :param key: The key identifying the element.
        :param identifier: The identifier of the element.
        :param all_values: All the values we have for the element.
        """
        # If we are not in an experiment, there is nothing to create.
        if not self._current_experiment:
            return

        # Checking whether the element is an undeclared experiment-ware.
        if key == 'experiment_ware' and not self._campaign_builder.has_experiment_ware_with_name(identifier):
            xp_ware_builder = self._campaign_builder.add_experiment_ware_builder()
            self._build_on_the_fly(xp_ware_builder, all_values, 'name', identifier)

        # Checking whether the element is an undeclared input.
        if key == 'input' and not self._campaign_builder.has_input_with_path(identifier):
            if self._input_set_builder is None:
                self._input_set_builder = self._campaign_builder.add_input_set_builder()
                self._input_set_builder['name'] = 'auto_name'
            input_builder = self._input_set_builder.add_input_builder()
            self._build_on_the_fly(input_builder, all_values, 'path', identifier)

    @staticmethod
    def _build_on_the_fly(builder: ModelBuilder, all_values: Dict[str, str],
                          element_key: str, element_id: str) -> None:
        """
        Creates an element of the campaign when it is first encountered while
        parsing an experiment (and was not encountered before).

        :param builder: The builder to use to build the element.
        :param all_values: All the values characterizing the element.
        :param element_key: The key that identifies the element in the builder.
        :param element_id: The identifier of the element.
        """
        for key, value in all_values.items():
            builder[key] = value
        builder[element_key] = element_id

    def get_campaign(self) -> Campaign:
        """
        Gives the campaign that has been read.

        :return: The read campaign.
        """
        return self._campaign_builder.build()
