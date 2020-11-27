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
This module provides all the models needed by the metrics project.
"""
from __future__ import annotations

from typing import Any

import jsonpickle

from metrics.core.constants import XP_WARE_NAME, CAMPAIGN_NAME, CAMPAIGN_TIMEOUT, CAMPAIGN_MEMOUT, CAMPAIGN_XP_WARES, \
    CAMPAIGN_INPUT_SET, CAMPAIGN_EXPERIMENTS, EXPERIMENT_INPUT, EXPERIMENT_XP_WARE, EXPERIMENT_CPU_TIME, INPUT_NAME, \
    INPUT_SET_NAME, INPUT_SET_INPUTS

"""
Global campaign attribute constants
"""


class Model:
    """
    Model is an abstract object giving basics behavior of this kind of object.
    """

    def __init__(self, log_data: dict) -> None:
        """
        Creates a new model.
        Updates the dictionary object with the log_data dictionary.
        @param log_data: dictionary to add to the current dictionary.
        """
        self.__dict__.update(log_data)

    def __getitem__(self, key: str) -> Any:
        """
        @param key: item key.
        @return: the value corresponding to the key from the dictionary.
        """
        return self.__dict__[key]

    def keys(self):
        """

        @return:
        """
        return self.__dict__.keys()


class ExperimentWare(Model):
    """
    This model corresponds to an experimentware.
    """

    def __init__(self, attributes: dict) -> None:
        """
        Set the obligatory values directly in the constructor and gives the rest to the parent constructor.
        @param attributes: dictionnary of attribute to add in this model
        """
        self.name = attributes.pop(XP_WARE_NAME)
        super().__init__(attributes)


class Campaign(Model):
    """
    This model corresponds to the campaign.
    """

    def __init__(self, attributes: dict) -> None:
        """
        Set the obligatory values directly in the constructor and gives the rest to the parent constructor.
        @param attributes: dictionnary of attribute to add in this model
        """
        self.name = attributes.pop(CAMPAIGN_NAME)
        self.timeout = attributes.pop(CAMPAIGN_TIMEOUT)
        self.memout = attributes.pop(CAMPAIGN_MEMOUT)
        self.experiment_wares = attributes.pop(CAMPAIGN_XP_WARES)
        self.input_set = attributes.pop(CAMPAIGN_INPUT_SET)
        self.experiments = attributes.pop(CAMPAIGN_EXPERIMENTS)
        super().__init__(attributes)

    def export(self):
        return jsonpickle.encode(self)

    def get_input_set(self):
        """

        @return:
        """
        return self.input_set

class Experiment(Model):
    """
    This model corresponds to an experiment.
    """

    def __init__(self, attributes: dict) -> None:
        """
        Set the obligatory values directly in the constructor and gives the rest to the parent constructor.
        @param attributes: dictionnary of attribute to add in this model
        """
        self.input = attributes.pop(EXPERIMENT_INPUT)
        self.experiment_ware = attributes.pop(EXPERIMENT_XP_WARE)
        self.cpu_time = attributes.pop(EXPERIMENT_CPU_TIME)
        super().__init__(attributes)


class Input(Model):
    """
    This model corresponds to an input.
    """

    def __init__(self, attributes: dict) -> None:
        """
        Set the obligatory values directly in the constructor and gives the rest to the parent constructor.
        @param attributes: dictionary of attribute to add in this model
        """
        self.name = attributes.pop(INPUT_NAME)
        super().__init__(attributes)


class InputSet(Model):
    """
    This model corresponds to the input set.
    """

    def __init__(self, attributes: dict) -> None:
        """
        Set the obligatory values directly in the constructor and gives the rest to the parent constructor.
        @param attributes: dictionnary of attribute to add in this model
        """
        self.name = attributes.pop(INPUT_SET_NAME)
        self.inputs = attributes.pop(INPUT_SET_INPUTS)
        super().__init__(attributes)

    def get_inputs(self):
        """

        @return:
        """
        return self.inputs