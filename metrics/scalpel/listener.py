###############################################################################
#                                                                             #
#  Scalpel - A Metrics Module                                                 #
#  Copyright (c) 2019-2021 - Univ Artois & CNRS, Exakis Nelite                #
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
#  See the GNU Lesser General Public License for more details.                #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this program.                                                   #
#  If not, see <https://www.gnu.org/licenses/>.                               #
#                                                                             #
###############################################################################


"""
This module provides a listener which listens to the events triggered while a
campaign is being parsed, and builds its representation based on these events.
"""


from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple, Union

from metrics.core.builder import CampaignBuilder
from metrics.core.builder.builder import InputSetBuilder, ModelBuilder
from metrics.core.constants import EXPERIMENT_INPUT, EXPERIMENT_XP_WARE
from metrics.core.constants import INPUT_NAME, INPUT_SET_NAME
from metrics.core.constants import XP_WARE_NAME
from metrics.core.model import Campaign

from metrics.scalpel.utils import logger


class KeyMapping:
    """
    The KeyMapping maps the keys defined in the campaign to parse to those
    expected by Scalpel.
    """

    def __init__(self) -> None:
        """
        Creates a new (empty) KeyMapping.
        """
        self._dict_representation = {}

    def __setitem__(self, scalpel_key: str,
                    campaign_key: Union[str, List[str]]) -> None:
        """
        Maps key(s) as defined in the campaign to a key that is expected by Scalpel.

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

        :return: A tuple having, as first element, the key expected by Scalpel,
                 or the given key if no mapping is set for this key and, as
                 second element, the number of values expected for this key.
        """
        for scalpel_key, campaign_keys in self._dict_representation.items():
            if campaign_key in campaign_keys:
                return scalpel_key, len(campaign_keys)
        return campaign_key, 1

    def get_sorted_keys(self, scalpel_key: str) -> List[str]:
        """
        Gives the list of the campaign keys that map to the given key expected
        by Scalpel.

        :param scalpel_key: The key expected by Scalpel.

        :return: The list of the campaign keys that map to the given key, in the
                 same order as that specified by the user.
        """
        campaign_keys = self._dict_representation.get(scalpel_key)
        if campaign_keys is None:
            return [scalpel_key]
        return campaign_keys


class AbstractCampaignParserListenerState:
    """
    The AbstractCampaignParserListenerState defines the (internal) state of a
    listener that is notified while parsing a campaign.
    """

    def __init__(self, listener: CampaignParserListener) -> None:
        """
        Creates a new AbstractCampaignParserListenerState.

        :param listener: The listener that is in this state.
        """
        self._listener = listener

    def log_data(self, builder: ModelBuilder, key: str,
                 sub_keys: List[str], read_values: Dict[str]) -> None:
        """
        Sets some read data to the given builder, and performs all the operations
        needed to preserve the consistency of the entire campaign while doing so.

        :param builder: The builder on which to set the read data.
        :param key: The key identifying the data to set.
        :param sub_keys: The keys identifying the elements of the data to set,
                         in the same order as that specified by the user.
        :param read_values: The values of the data to set.
        """
        name = ' '.join('' if read_values.get(v) is None else read_values.get(v) for v in sub_keys)
        self._create_if_missing(key, name, read_values)
        logger.trace(f'logging {name} as {key}')
        builder[key] = name

    def _create_if_missing(self, key: str, identifier: str, all_values: Dict[str]) -> None:
        """
        Creates (or not) an element of the campaign that is being parsed if no corresponding
        element with the given identifier has already been encountered in this campaign.

        :param key: The key identifying the element to create if needed.
        :param identifier: The identifier of the element to create if needed.
        :param all_values: The values that have been read about the element.
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
        Does NOT create an element of the campaign that is being parsed if no
        corresponding element with the given identifier has already been encountered
        in this campaign.

        :param key: The key identifying the element to create if needed.
        :param identifier: The identifier of the element to create if needed.
        :param all_values: The values that have been read about the element.
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
        :param all_values: The values that have been read about the element.
        """
        builder = self._listener.get_campaign_builder()
        if key == EXPERIMENT_INPUT:
            self._create_input_if_missing(builder, identifier, all_values)
        elif key == EXPERIMENT_XP_WARE:
            self._create_experiment_ware_if_missing(builder, identifier, all_values)

    def _create_experiment_ware_if_missing(self, campaign_builder: CampaignBuilder,
                                           name: str, all_values: Dict[str, str]) -> None:
        """
        Creates an experiment-ware if no experiment-ware with the given name
        has already been encountered in the campaign that is being parsed.

        :param campaign_builder: The builder of the campaign that is being parsed.
        :param name: The name of the experiment-ware to create if needed.
        :param all_values: The values that have been read about the experiment-ware.
        """
        # If the inferred name corresponds to an existing experiment-ware, there is nothing to do.
        if campaign_builder.has_experiment_ware_with_name(name):
            return

        # This is the first time we read this experiment-ware: we need to create it on the fly.
        xp_ware_builder = campaign_builder.add_experiment_ware_builder()
        InExperimentCampaignParserListenerState._build_on_the_fly(xp_ware_builder, XP_WARE_NAME,
                                                                  name, all_values)

    def _create_input_if_missing(self, campaign_builder: CampaignBuilder,
                                 name: str, all_values: Dict[str, str]) -> None:
        """
        Creates an input if no input with the given name has already been
        encountered in the campaign that is being parsed.

        :param campaign_builder: The builder of the campaign that is being parsed.
        :param name: The name of the input to create if needed.
        :param all_values: The values that have been read about the input.
        """
        # If the inferred name corresponds to an existing input, there is nothing to do.
        if campaign_builder.has_input_with_name(name):
            return

        # This is the first time we read this input: we need to create it on the fly.
        input_set_builder = self._listener.get_input_set_builder('auto_name')
        input_builder = input_set_builder.add_input_builder()
        InExperimentCampaignParserListenerState._build_on_the_fly(input_builder, INPUT_NAME,
                                                                  name, all_values)

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
        # Setting the element id.
        logger.trace(f'building on the fly {element_key} with value {element_id}')
        builder[element_key] = element_id

        # If there is only one read value, then there is nothing more to do.
        if len(all_values) == 1:
            return

        # Setting all remaining data about the element to build.
        for key, value in all_values.items():
            if key == element_key:
                builder[f'original_{key}'] = value
            else:
                builder[key] = value


class CampaignParserListener:
    """
    The CampaignParserListener is a listener notified while parsing a campaign.
    """

    def __init__(self) -> None:
        """
        Creates a new CampaignParserListener.
        """
        self._key_mapping = KeyMapping()
        self._default_values = {}
        self._ignored_data = set()
        self._campaign_builder = None
        self._input_set_builder = None
        self._current_builder = None
        self._state = DefaultCampaignParserListenerState(self)
        self._pending_keys = defaultdict(dict)
        self._logged_keys = set()

    def add_key_mapping(self, scalpel_key: str,
                        campaign_key: Union[str, List[str]]) -> None:
        """
        Maps key(s) as defined in the campaign to a key that is expected by Scalpel.

        :param scalpel_key: The key expected by Scalpel.
        :param campaign_key: The key(s) defined in the campaign.
        """
        self._key_mapping[scalpel_key] = campaign_key

    def add_default_value(self, key: str, value: str) -> None:
        """
        Adds a default value to set for the specified key when missing from an experiment.

        :param key: The key to add a default value for.
        :param value: The default value for the key.
        """
        self._default_values[key] = value

    def add_ignored_data(self, key: str) -> None:
        """
        Specifies that some data must be ignored instead of being logged.

        :param key: The key identifying the data to ignore.
        """
        self._ignored_data.add(key)

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
        logger.trace('starting to parse the campaign')
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

        :raises ValueError: If some keys are still pending for the current campaign.
        """
        self._commit_pending_keys()
        self._current_builder.check_if_complete()
        self._current_builder = None
        logger.trace('campaign has been parsed')

    def start_experiment_ware(self) -> None:
        """
        Notifies this listener that a new experiment-ware is going to be parsed.
        """
        logger.trace('starting to parse an experiment-ware')
        self._current_builder = self._campaign_builder.add_experiment_ware_builder()

    def end_experiment_ware(self) -> None:
        """
        Notifies this listener that the current experiment-ware has been
        fully parsed.
        """
        self._commit_pending_keys()
        self._current_builder.check_if_complete()
        self._current_builder = self._campaign_builder
        logger.trace('experiment-ware has been parsed')

    def start_input_set(self) -> None:
        """
        Notifies this listener that a new input set is going to be parsed.
        """
        logger.trace('starting to parse an input-set')
        self._input_set_builder = self._campaign_builder.add_input_set_builder()
        self._current_builder = self._input_set_builder

    def get_input_set_builder(self, default_name: str) -> InputSetBuilder:
        """
        Gives the input set builder used by this listener to create the input
        set(s) and the inputs of the campaign being parsed.
        If an input set builder has not already been set, an input set builder with
        the given name is created.

        :param default_name: The name of the input set builder to create, if needed.

        :return: The input set builder to use for the campaign.
        """
        if self._input_set_builder is None:
            self._input_set_builder = self._campaign_builder.add_input_set_builder()
            self._input_set_builder[INPUT_SET_NAME] = default_name
        return self._input_set_builder

    def end_input_set(self) -> None:
        """
        Notifies this listener that the current input set has been fully parsed.
        """
        self._commit_pending_keys()
        self._current_builder.check_if_complete()
        self._input_set_builder = None
        self._current_builder = self._campaign_builder
        logger.trace('input-set has been parsed')

    def start_input(self) -> None:
        """
        Notifies this listener that a new input is going to be parsed.
        """
        logger.trace('starting to parse an input')
        self._current_builder = self._input_set_builder.add_input_builder()

    def end_input(self) -> None:
        """
        Notifies this listener that the current input has been fully parsed.
        """
        self._commit_pending_keys()
        self._current_builder.check_if_complete()
        self._current_builder = self._input_set_builder
        logger.trace('input has been parsed')

    def start_experiment(self) -> None:
        """
        Notifies this listener that a new experiment is going to be parsed.
        """
        logger.trace('starting to parse an experiment')
        self._current_builder = self._campaign_builder.add_experiment_builder()
        self._state = InExperimentCampaignParserListenerState(self)
        self._logged_keys.clear()

    def end_experiment(self) -> None:
        """
        Notifies this listener that the current experiment has been fully parsed.
        """
        # Completing the missing values for the experiment.
        for key, value in self._default_values.items():
            if key not in self._logged_keys:
                logger.debug(f'using default value for {key}')
                self.log_data(key, value)
        self._commit_pending_keys()
        self._current_builder.check_if_complete()

        # Switching to the "out-of-experiment" state.
        self._current_builder = self._campaign_builder
        self._state = DefaultCampaignParserListenerState(self)
        logger.trace('experiment has been parsed')

    def log_data(self, key: str, value: Any) -> None:
        """
        Notifies this listener about data that has been read.
        This data is set to the element of the campaign that is currently
        being built.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        # Checking whether the logged data is relevant.
        if key in self._ignored_data:
            logger.trace(f'ignoring {value} for {key}')
            return

        # Saving the logged data.
        logger.trace(f'{value} read for {key}')
        scalpel_key, nb_keys = self._key_mapping[key]
        read_values = self._pending_keys[scalpel_key]
        read_values[key] = str(value)
        self._logged_keys.add(key)
        if len(read_values) == nb_keys:
            self._commit_key(scalpel_key, read_values)
            del self._pending_keys[scalpel_key]

    def _commit_key(self, scalpel_key: str, read_values: Dict[str]) -> None:
        """
        Commits the values read for the given key.

        :param scalpel_key: The key to commit.
        :param read_values: The values that have been read for the key.
        """
        if self._key_mapping[scalpel_key][0] == scalpel_key:
            logger.trace(f'validating {scalpel_key}')
            if len(read_values.keys()) == 1 and scalpel_key in read_values.keys():
                self._state.log_data(self._current_builder, scalpel_key, [scalpel_key], read_values)
                self._logged_keys.add(scalpel_key)
            else:
                sub_keys = self._key_mapping.get_sorted_keys(scalpel_key)
                self._state.log_data(self._current_builder, scalpel_key, sub_keys, read_values)
                self._logged_keys.add(scalpel_key)
        else:
            logger.trace(f'remapping {scalpel_key}')
            sub_keys = self._key_mapping.get_sorted_keys(scalpel_key)
            value = ' '.join('' if read_values.get(v) is None else read_values.get(v) for v in sub_keys)
            self.log_data(scalpel_key, value)

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
            logger.warning(f'logging incomplete value for "{key}": {value}')
            self._commit_key(key, value)
        self.log_data('incomplete', True)
        self._pending_keys.clear()

    def get_campaign(self) -> Campaign:
        """
        Gives the campaign that has been read.

        :return: The read campaign.
        """
        return self._campaign_builder.build()
