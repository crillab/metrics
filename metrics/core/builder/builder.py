###############################################################################
#                                                                             #
#  Core - A Metrics Module                                                    #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                #
#  -------------------------------------------------------------------------- #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  Core - Core components for Metrics                                         #
#                                                                             #
#                                                                             #
#  This program is free software: you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation, either version 3    of the License, or (at your #
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
This module provides classes for building each model of the metrics-core.
"""

from __future__ import annotations

from typing import Any

from metrics.core.builder.attribute_manager import AttributeManager, AttributeManagerSet
from metrics.core.builder.typing_strategy import TypingStrategyEnum
from metrics.core.model import ExperimentWare, Campaign, Experiment, Input, InputSet, Model
from metrics.core.constants import XP_WARE_NAME, CAMPAIGN_NAME, CAMPAIGN_TIMEOUT, CAMPAIGN_MEMOUT, CAMPAIGN_XP_WARES, \
    CAMPAIGN_INPUT_SET, CAMPAIGN_EXPERIMENTS, EXPERIMENT_INPUT, EXPERIMENT_XP_WARE, EXPERIMENT_CPU_TIME, INPUT_NAME, \
    INPUT_SET_NAME, INPUT_SET_INPUTS


class ValueManager:
    """
    The ValueManager permits to manage the attribute value of the future model.
    We can add one or many values inside and return a simple value or a list.
    """

    def __init__(self, attribute_manager: AttributeManager):
        """
        Creates a new ValueManager.
        @param attribute_manager: The attribute manager that permits to verify the value of this ValueManager.
        """
        self._elt = list()
        self._attribute_manager = attribute_manager

    def add(self, value: Any) -> None:
        """
        Adds a new value or list of values to the value manager.
        @param value: the value to add.
        """
        values = value if isinstance(value, list) else [value]
        for val in values:
            self._add_element(val)

    def _add_element(self, value: Any) -> None:
        self._attribute_manager.verify(value)
        self._elt.append(value)

    def get_value(self) -> Any:
        """

        @return: the single value or a list of values depending of what it has been added.
        """
        elt = [self._attribute_manager.parse(e) for e in self._elt]
        if not self._attribute_manager.empty and not elt:
            raise TypeError(f'{self._attribute_manager.name} must contain at least one element.')
        if not elt:
            return None
        return elt if len(elt) > 1 or self._attribute_manager.is_list else elt[0]

    def __str__(self):
        return str(self._elt)


class ModelBuilder:
    """
    ModelBuilder is an abstract object that permits to generalize mechanism of each builders.
    """

    def __init__(self, model: type, attribute_manager_set: AttributeManagerSet) -> None:
        """
        Create a new ModelBuilder.
        @param model: is the model that is build when build() is called.
        @param attribute_manager_set: is the set of attribute managers that will manage value of each model attributes.
        """
        self._log_data = dict()
        for attr in attribute_manager_set.attribute_managers:
            self._log_data[attr.name] = ValueManager(attr)
        self._model = model
        self._attribute_manager_set = attribute_manager_set

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Permits to add a new value to an existing or not item.
        If it is not existing, it creates a new attribute manager in the attribute set manager and use it.
        @param key: key of the item.
        @param value: value to add to the item.
        """
        if key not in self._log_data:
            attr = self._attribute_manager_set.add_attribute_manager_for_typing_finder(name=key)
            self._log_data[attr.name] = ValueManager(attr)
        self._log_data[key].add(value)

    def build(self) -> Model:
        """
        Builds the model verifying if all the constraints are respected.
        @return: the builded model.
        """
        return self._model(self._get_final_data())

    def check_if_complete(self):
        """
        Verifies if all the constraints are respected.
        """
        for value in self._log_data.values():
            value.get_value()

    def _get_final_data(self) -> dict:
        return {
            key: value.get_value() for key, value in self._log_data.items()
        }


class CampaignBuilder(ModelBuilder):
    """
    A campaign builder is the global builder containing all what we need to create a campaign and their children
    attributes.
    """

    def __init__(self):
        """
        Creates a campaign builder.
        It associates to the builder the attribute manager sets.
        """
        attribute_manager_sets = AttributeManagerSets()
        super().__init__(Campaign, attribute_manager_sets.campaign_attr_set)
        self._attribute_manager_sets = attribute_manager_sets

    def add_experiment_ware_builder(self) -> ExperimentWareBuilder:
        """
        Adds a new experimentware builder to the list of experimentware builders.
        It gives to its constructor the experimentware attribute set.
        @return: the created experimentware builder.
        """
        experiments_ware = self[CAMPAIGN_XP_WARES] = ExperimentWareBuilder(
            self._attribute_manager_sets.xp_ware_attr_set)
        return experiments_ware

    def add_experiment_builder(self) -> ExperimentBuilder:
        """
        Adds a new experiment builder to the list of experiment builders.
        It gives to its constructor the experiment attribute set.
        @return: the created experiment builder.
        """
        experiment = self[CAMPAIGN_EXPERIMENTS] = ExperimentBuilder(self._attribute_manager_sets.xp_attr_set)
        return experiment

    def add_input_set_builder(self) -> InputSetBuilder:
        """
        Adds a new input set builder.
        It gives to its constructor the input set attribute set.
        @return: the created input set builder.
        """
        input_set = self[CAMPAIGN_INPUT_SET] = InputSetBuilder(self._attribute_manager_sets.input_set_attr_set,
                                                        self._attribute_manager_sets.input_attr_set)
        return input_set

    def has_experiment_ware_with_name(self, param):
        return not self._attribute_manager_sets.xp_ware_attr_set.get_attribute_manager(XP_WARE_NAME).is_unique(param)

    def has_input_with_name(self, param):
        return not self._attribute_manager_sets.input_attr_set.get_attribute_manager(INPUT_NAME).is_unique(param)


class ExperimentWareBuilder(ModelBuilder):
    """
    An experimentware builder manage the building of an experimentware model.
    """

    def __init__(self, attribute_manager_set: AttributeManagerSet):
        """
        Creates an experimentware builder.
        @param attribute_manager_set: the attribute manager set that will manage values of attributes.
        """
        super().__init__(ExperimentWare, attribute_manager_set)


class ExperimentBuilder(ModelBuilder):
    """
    An experiment builder manage the building of an experiment model.
    """

    def __init__(self, attribute_manager_set: AttributeManagerSet):
        """
        Creates an experiment builder.
        @param attribute_manager_set: the attribute manager set that will manage values of attributes.
        """
        super().__init__(Experiment, attribute_manager_set)


class InputSetBuilder(ModelBuilder):
    """
    An input set builder manage the building of an input set model.
    """

    def __init__(self, attribute_manager_set: AttributeManagerSet, input_attribute_set: AttributeManagerSet):
        """
        Creates an input set builder.
        @param attribute_manager_set: the attribute manager set that will manage values of attributes.
        @param input_attribute_set: the input attribute set needed for each future create input.
        """
        super().__init__(InputSet, attribute_manager_set)
        self._input_attribute_set = input_attribute_set

    def add_input_builder(self) -> InputBuilder:
        """
        Adds a new input builder to the list of input builders.
        It gives to its constructor the input attribute set.
        @return: the created input builder.
        """
        input = self['inputs'] = InputBuilder(self._input_attribute_set)
        return input

    def has_input_with_path(self, param):
        return not self._input_attribute_set.get_attribute_manager(INPUT_NAME).is_unique(param)


class InputBuilder(ModelBuilder):
    """
    An input builder manage the building of an input model.
    """

    def __init__(self, attribute_manager_set: AttributeManagerSet):
        """
        Creates an input builder.
        @param attribute_manager_set: the attribute manager set that will manage values of attributes.
        """
        super().__init__(Input, attribute_manager_set)


class AttributeManagerSets:
    """
    The main object that will manage all the attributes of each model builder.
    """

    def __init__(self):
        """
        Creates an AttributeManagerSets object that instantiates the attribute manager set for each model builder
        """
        self._input_attr_set = AttributeManagerSet()
        self._input_set_attr_set = AttributeManagerSet()
        self._campaign_attr_set = AttributeManagerSet()
        self._xp_ware_attr_set = AttributeManagerSet()
        self._xp_attr_set = AttributeManagerSet()

        self._init_campaign_builder_attribute_set()
        self._init_input_set_builder_attribute_set()
        self._init_input_builder_attribute_set()
        self._init_experiment_ware_builder_attribute_set()
        self._init_experiment_builder_attribute_set()

    def _init_campaign_builder_attribute_set(self):
        self._campaign_attr_set.add_attribute_manager_for_typing(name=CAMPAIGN_NAME,
                                                                 ordered_typing=[TypingStrategyEnum.STRING],
                                                                 is_list=False, empty=False,
                                                                 nullable=False)
        self._campaign_attr_set.add_attribute_manager_for_typing(name=CAMPAIGN_TIMEOUT,
                                                                 ordered_typing=[TypingStrategyEnum.FLOAT],
                                                                 is_list=False, empty=False,
                                                                 nullable=False)
        self._campaign_attr_set.add_attribute_manager_for_typing(name=CAMPAIGN_MEMOUT,
                                                                 ordered_typing=[TypingStrategyEnum.FLOAT],
                                                                 is_list=False, empty=False,
                                                                 nullable=False)
        self._campaign_attr_set.add_attribute_manager_for_builder(name=CAMPAIGN_XP_WARES,
                                                                  builder_type=ExperimentWareBuilder,
                                                                  is_list=True, empty=False,
                                                                  nullable=False)
        self._campaign_attr_set.add_attribute_manager_for_builder(name=CAMPAIGN_INPUT_SET, builder_type=InputSetBuilder,
                                                                  is_list=False,
                                                                  empty=False,
                                                                  nullable=False)
        self._campaign_attr_set.add_attribute_manager_for_builder(name=CAMPAIGN_EXPERIMENTS, builder_type=ExperimentBuilder,
                                                                  is_list=True,
                                                                  empty=False,
                                                                  nullable=False)

    def _init_input_set_builder_attribute_set(self):
        self._input_set_attr_set.add_attribute_manager_for_typing(name=INPUT_SET_NAME,
                                                                  ordered_typing=[TypingStrategyEnum.STRING],
                                                                  is_list=False, empty=False,
                                                                  nullable=False)
        self._input_set_attr_set.add_attribute_manager_for_builder(name=INPUT_SET_INPUTS, builder_type=InputBuilder,
                                                                   is_list=True,
                                                                   empty=False,
                                                                   nullable=False)

    def _init_input_builder_attribute_set(self):
        self._input_attr_set.add_attribute_manager_for_typing(name=INPUT_NAME, ordered_typing=[TypingStrategyEnum.STRING],
                                                              is_list=False, empty=False,
                                                              nullable=False, unique=True)

    def _init_experiment_ware_builder_attribute_set(self):
        self._xp_ware_attr_set.add_attribute_manager_for_typing(name=XP_WARE_NAME, ordered_typing=[TypingStrategyEnum.STRING],
                                                                is_list=False, empty=False,
                                                                nullable=False, unique=True)

    def _init_experiment_builder_attribute_set(self):
        self._xp_attr_set.add_attribute_manager_for_typing(name=EXPERIMENT_INPUT, ordered_typing=[TypingStrategyEnum.STRING],
                                                           is_list=False,
                                                           empty=False,
                                                           nullable=False)
        self._xp_attr_set.add_attribute_manager_for_typing(name=EXPERIMENT_XP_WARE,
                                                           ordered_typing=[TypingStrategyEnum.STRING],
                                                           is_list=False, empty=False,
                                                           nullable=False)
        self._xp_attr_set.add_attribute_manager_for_typing(name=EXPERIMENT_CPU_TIME, ordered_typing=[TypingStrategyEnum.FLOAT],
                                                           is_list=False, empty=False,
                                                           nullable=False)

    @property
    def input_attr_set(self):
        """

        @return: the attribute manager for inputs
        """
        return self._input_attr_set

    @property
    def input_set_attr_set(self):
        """

        @return: the attribute manager for input set
        """
        return self._input_set_attr_set

    @property
    def campaign_attr_set(self):
        """

        @return: the attribute manager for campaign
        """
        return self._campaign_attr_set

    @property
    def xp_ware_attr_set(self):
        """

        @return: the attribute manager for experimentwares
        """
        return self._xp_ware_attr_set

    @property
    def xp_attr_set(self):
        """

        @return: the attribute manager for experiments
        """
        return self._xp_attr_set
