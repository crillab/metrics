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


class ExperimentWare(Model):
    """
    This model corresponds to an experimentware.
    """

    def __init__(self, attributes: dict) -> None:
        """
        Set the obligatory values directly in the constructor and gives the rest to the parent constructor.
        @param attributes: dictionnary of attribute to add in this model
        """
        self.name = attributes.pop('name')
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
        self.name = attributes.pop('name')
        self.timeout = attributes.pop('timeout')
        self.memout = attributes.pop('memout')
        self.experiment_wares = attributes.pop('experiment_wares')
        self.input_set = attributes.pop('input_set')
        self.experiments = attributes.pop('experiments')
        super().__init__(attributes)

    def export(self):
        return jsonpickle.encode(self)


class Experiment(Model):
    """
    This model corresponds to an experiment.
    """

    def __init__(self, attributes: dict) -> None:
        """
        Set the obligatory values directly in the constructor and gives the rest to the parent constructor.
        @param attributes: dictionnary of attribute to add in this model
        """
        self.input = attributes.pop('input')
        self.experiment_ware = attributes.pop('experiment_ware')
        self.cpu_time = attributes.pop('cpu_time')
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
        self.path = attributes.pop('path')
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
        self.name = attributes.pop('name')
        self.inputs = attributes.pop('inputs')
        super().__init__(attributes)


