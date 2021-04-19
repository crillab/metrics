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


from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple, Union
from warnings import warn

from metrics.core.builder import CampaignBuilder
from metrics.core.builder.builder import ModelBuilder, InputSetBuilder
from metrics.core.constants import EXPERIMENT_XP_WARE, EXPERIMENT_INPUT, XP_WARE_NAME, INPUT_NAME, INPUT_SET_NAME
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


class AbstractCampaignParserListenerState:
    """
    The AbstractCampaignParserListenerState defines the state of a listener
    that is notified while parsing a campaign.
    """

    def __init__(self, listener: CampaignParserListener) -> None:
        """
        Creates a new AbstractCampaignParserListenerState.

        :param listener: The listener that is in this state.
        """
        self._listener = listener

    def log_data(self, builder: ModelBuilder, key: str, sub_keys: List[str], read_values: Dict[str]) -> None:
        """
        Sets read data to the given builder, and performs all the operations
        needed to preserve the consistency of the entire campaign while
        doing so.

        :param builder: The builder on which to set the read data.
        :param key: The key identifying the data to set.
        :param sub_keys: The keys identifying the elements of the data to set,
                         in the same order as that specified by the user.
        :param read_values: The values of the data to set.
        """
        identifier = ' '.join('' if read_values.get(v) is None else read_values.get(v) for v in sub_keys)
        self._create_if_missing(key, identifier, read_values)
        builder[key] = identifier

    def _create_if_missing(self, key: str, identifier: str, all_values: Dict[str]) -> None:
        """
        Creates (or not) an element of the campaign that is being parsed if no element
        with the given identifier has already been encountered in this campaign.

        :param key: The key identifying the element to create if needed.
        :param identifier: The identifier of the element to create if needed.
        :param all_values: The values that has been read about the element.
        """
        raise NotImplementedError('Method "_create_if_missing()" is abstract!')


class DefaultCampaignParserListenerState(AbstractCampaignParserListenerState):
    """
    The DefaultCampaignParserListenerState is the state of a listener that
    does not ensure anything regarding the consistency of the campaign that
    is being parsed.
    """

    def _create_if_missing(self, key: str, identifier: str, all_values: Dict[str]) -> None:
        """
        Does NOT create an element of the campaign that is being parsed if no element
        with the given identifier has already been encountered in this campaign.

        :param key: The key identifying the element to create if needed.
        :param identifier: The identifier of the element to create if needed.
        :param all_values: The values that has been read about the element.
        """


class InExperimentCampaignParserListenerState(AbstractCampaignParserListenerState):
    """
    The InExperimentCampaignParserListenerState is the state of a listener that
    ensures the consistency of the campaign regarding the data read about an
    experiment.
    """

    def _create_if_missing(self, key: str, identifier: str, all_values: Dict[str, str]) -> None:
        """
        Creates an element of the campaign that is being parsed if no element
        with the given identifier has already been encountered in this
        campaign.

        :param key: The key identifying the element to create if needed.
        :param identifier: The identifier of the element to create if needed.
        :param all_values: The values that has been read about the element.
        """
        builder = self._listener.get_campaign_builder()
        if key == EXPERIMENT_XP_WARE:
            InExperimentCampaignParserListenerState._create_experiment_ware_if_missing(builder, identifier, all_values)
        elif key == EXPERIMENT_INPUT:
            self._create_input_if_missing(builder, identifier, all_values)

    @staticmethod
    def _create_experiment_ware_if_missing(campaign_builder: CampaignBuilder,
                                           name: str, all_values: Dict[str, str]) -> None:
        """
        Creates an experiment-ware if no experiment-ware with the given name
        has already been encountered in the campaign that is being parsed.

        :param campaign_builder: The builder of the campaign that is being parsed.
        :param name: The name of the experiment-ware to create if needed.
        :param all_values: The values that has been read about the experiment-ware.
        """
        # If the name has been read and corresponds to an existing experiment-ware, there is nothing to do.
        if XP_WARE_NAME in all_values and campaign_builder.has_experiment_ware_with_name(all_values[XP_WARE_NAME]):
            return

        # If the inferred name corresponds to an existing experiment-ware, there is nothing to do.
        if campaign_builder.has_experiment_ware_with_name(name):
            return

        # This is the first time we read this experiment-ware: we need to create it on the fly.
        xp_ware_builder = campaign_builder.add_experiment_ware_builder()
        InExperimentCampaignParserListenerState._build_on_the_fly(xp_ware_builder, XP_WARE_NAME, name, all_values)

    def _create_input_if_missing(self, campaign_builder: CampaignBuilder,
                                 name: str, all_values: Dict[str, str]) -> None:
        """
        Creates an input if no input with the given name has already been
        encountered in the campaign that is being parsed.

        :param campaign_builder: The builder of the campaign that is being parsed.
        :param name: The name of the input to create if needed.
        :param all_values: The values that has been read about the input.
        """
        # If the name has been read and corresponds to an existing input, there is nothing to do.
        if INPUT_NAME in all_values and campaign_builder.has_input_with_name(all_values[INPUT_NAME]):
            return

        # If the inferred name corresponds to an existing input, there is nothing to do.
        if campaign_builder.has_input_with_name(name):
            return

        # This is the first time we read this input: we need to create it on the fly.
        input_set_builder = self._listener.get_input_set_builder('auto_name')
        input_builder = input_set_builder.add_input_builder()
        InExperimentCampaignParserListenerState._build_on_the_fly(input_builder, INPUT_NAME, name, all_values)

    @staticmethod
    def _build_on_the_fly(builder: ModelBuilder, element_key: str, element_id: str,
                          all_values: Dict[str, str]) -> None:
        """
        Creates an element of the campaign when it is first encountered while
        parsing an experiment (and was not encountered before).

        :param builder: The builder to use to build the element.
        :param element_key: The key that identifies the element in the builder.
        :param element_id: The identifier of the element.
        :param all_values: All the values characterizing the element.
        """
        # If there is only one read value, then this value is the identifier.
        if len(all_values) == 1:
            builder[element_key] = element_id
            return

        # Setting up all data about the element to build.
        element_key_already_declared = False
        for key, value in all_values.items():
            if key == element_key:
                element_key_already_declared = True
            builder[key] = value

        # The (inferred) identifier is only set when it has not been read.
        if not element_key_already_declared:
            builder[element_key] = element_id


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
        self._state = DefaultCampaignParserListenerState(self)
        self._pending_keys = defaultdict(dict)

    def add_key_mapping(self, scalpel_key: str,
                        campaign_key: Union[str, List[str]]) -> None:
        """
        Maps key(s) as defined in the campaign to that expected by Scalpel.

        :param scalpel_key: The key expected by Scalpel.
        :param campaign_key: The key(s) defined in the campaign.
        """
        self._key_mapping[scalpel_key] = campaign_key

    def get_mapping(self, scalpel_key: str) -> List[str]:
        """
        Gives the mapping for the given Scalpel key.

        :param scalpel_key: The key expected by Scalpel.
        """
        return self._key_mapping.get_sorted_keys(scalpel_key)

    def start_campaign(self) -> None:
        """
        Notifies this listener that a new campaign is going to be parsed.
        """
        self._campaign_builder = CampaignBuilder()
        self._current_builder = self._campaign_builder

    def get_campaign_builder(self) -> CampaignBuilder:
        """
        Gives the builder used by this listener to create the campaign that is
        being parsed.

        :return: The builder of the campaign being parsed.
        """
        return self._campaign_builder

    def end_campaign(self) -> None:
        """
        Notifies this listener that the current campaign has been fully parsed.

        :raises ValueError: If some keys are still pending for the current
                            campaign.
        """
        self._current_builder.check_if_complete()
        self._commit_pending_keys()
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
        self._current_builder.check_if_complete()
        self._commit_pending_keys()
        self._current_builder = self._campaign_builder

    def start_input_set(self) -> None:
        """
        Notifies this listener that a new input set is going to be parsed.
        """
        self._input_set_builder = self._campaign_builder.add_input_set_builder()
        self._current_builder = self._input_set_builder

    def get_input_set_builder(self, name: str) -> InputSetBuilder:
        """
        Gives the input set builder used by this listener to create the input
        set and inputs of the campaign being parsed.
        If the input set builder does not exist, an input set builder with the
        given name is created.

        :param name: The name of the input set builder to create, if needed.

        :return: The input set builder to use for the campaign.
        """
        if self._input_set_builder is None:
            self._input_set_builder = self._campaign_builder.add_input_set_builder()
            self._input_set_builder[INPUT_SET_NAME] = name
        return self._input_set_builder

    def end_input_set(self) -> None:
        """
        Notifies this listener that the current input set has been fully parsed.
        """
        self._current_builder.check_if_complete()
        self._commit_pending_keys()
        self._input_set_builder = None
        self._current_builder = self._campaign_builder

    def start_input(self) -> None:
        """
        Notifies this listener that a new input is going to be parsed.
        """
        self._current_builder = self._input_set_builder.add_input_builder()

    def end_input(self) -> None:
        """
        Notifies this listener that the current input has been fully parsed.
        """
        self._current_builder.check_if_complete()
        self._commit_pending_keys()
        self._current_builder = self._input_set_builder

    def start_experiment(self) -> None:
        """
        Notifies this listener that a new experiment is going to be parsed.
        """
        self._current_builder = self._campaign_builder.add_experiment_builder()
        self._state = InExperimentCampaignParserListenerState(self)

    def end_experiment(self) -> None:
        """
        Notifies this listener that the current experiment has been
        fully parsed.
        """
        self._current_builder.check_if_complete()
        self._commit_pending_keys()
        self._current_builder = self._campaign_builder
        self._state = DefaultCampaignParserListenerState(self)

    def log_data(self, key: str, value: Any) -> None:
        """
        Notifies this listener about data that has been read.
        This data is set to the element of the campaign that is currently
        being built.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        scalpel_key, nb = self._key_mapping[key]
        read_values = self._pending_keys[scalpel_key]
        read_values[key] = str(value)
        if len(read_values) == nb:
            self._commit_key(scalpel_key, read_values)
            del self._pending_keys[scalpel_key]

    def log_metadata(self, key: str, value: Any) -> None:
        """
        Notifies this listener about data that has been read.
        This data is set to the campaign.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        self._campaign_builder[key] = str(value)

    def _commit_key(self, scalpel_key: str, read_values: Dict[str]) -> None:
        """
        Commits the values read for the given key.

        :param scalpel_key: The key to commit.
        :param read_values: The values that have been read for the key.
        """
        sub_keys = self._key_mapping.get_sorted_keys(scalpel_key)
        self._state.log_data(self._current_builder, scalpel_key, sub_keys, read_values)

    def _commit_pending_keys(self) -> None:
        """
        Commits the values for the keys that have not been committed yet.
        If such keys exist, a warning is raised, as it means that values
        are missing for this key.
        """
        # If there is no pending key, everything is fine.
        if len(self._pending_keys) == 0:
            return

        # Otherwise, we commit the remaining keys, and warn the user.
        for key, value in self._pending_keys.items():
            warn(f'Logging incomplete value for "{key}": {value}')
            self._commit_key(key, value)
        self.log_data('incomplete', True)
        self._pending_keys = defaultdict(dict)

    def get_campaign(self) -> Campaign:
        """
        Gives the campaign that has been read.

        :return: The read campaign.
        """
        return self._campaign_builder.build()
