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
This module provides classes permiting to manage attributes of model builders.
"""

from typing import Any, List

from metrics.core.builder.typing_strategy import TypingStrategy, TypingStrategyEnum


class AttributeManager:
    """
    AttributeManager is an abstract object to manage a specific attribute through many instantiations of a same object.
    It permits to verify if the attribute respect all the constraints and also to build or parse it at the end.
    """

    def __init__(self, name: str, is_list: bool, empty: bool, nullable: bool):
        """
        Creates a new AttributeManager.
        @param name: the attribute name of the object where this attribute manager is used.
        @param is_list: True if the attribute need to be a list.
        @param empty: True if this attribute could be empty.
        @param nullable: True if this attribute could equal to None.
        """
        self._is_list = is_list
        self._empty = empty
        self._nullable = nullable
        self._name = name

    @property
    def name(self):
        """

        @return: the name of the managed attribute.
        """
        return self._name

    @property
    def nullable(self):
        """

        @return: True if the attribute could be equal to None.
        """
        return self._nullable

    @property
    def empty(self):
        """

        @return: True if the attribute could be empty.
        """
        return self._empty

    @property
    def is_list(self):
        """

        @return: True if the attribute needs to be a list.
        """
        return self._is_list

    def verify(self, obj: Any) -> None:
        """
        Verify the conformity of the object.
        @param obj: object to be tested by the attribute manager.
        """
        raise NotImplementedError('This abstract method needs to be implemented.')

    def parse(self, obj: Any) -> Any:
        """
        Parse the object that has been previously verified.
        @param obj: obj to parse.
        @return: parsed object.
        """
        raise NotImplementedError('This abstract method needs to be implemented.')


class AttributeManagerForBuilder(AttributeManager):
    """
    AttributeManager specialised for builder attributes (e.g. InputSetBuilder has an attribute which is a list of InputBuilder).
    """

    def __init__(self, name: str, builder_type: type, is_list: bool, empty: bool, nullable: bool):
        """
        Creates a new AttributeManager for Builder.
        @param name: the attribute name of the object where this attribute manager is used.
        @param builder_type: the type of the builder.
        @param is_list: True if the attribute need to be a list.
        @param empty: True if this attribute could be empty.
        @param nullable: True if this attribute could equal to None.
        """
        super().__init__(name, is_list, empty, nullable)
        self._builder_type = builder_type

    def verify(self, obj: Any) -> None:
        """
        Verify the type of the object (that must corresponds to the builder type given at construction).
        @param obj: object to test.
        """
        if not isinstance(obj, self._builder_type):
            raise TypeError(f'{self._name} is not matching type {self._builder_type}.')

    def parse(self, obj: Any) -> Any:
        """
        Parsing is simple: object is builded.
        @param obj: object to build.
        @return: the object builded.
        """
        return obj.build()


class AttributeManagerForTyping(AttributeManager):
    """
    AttributeManagerForTyping permits to manage an attribute trying to parse it with TypingStrategies given.
    AttributeManagerForTyping makes attention to give the same typing to all attributes where this attribute manager is associated.
    """

    def __init__(self, name: str, ordered_typing: List[TypingStrategy], is_list: bool, empty: bool, nullable: bool, unique: bool):
        """
        Creates a new AttributeManager for Builder.
        @param name: the attribute name of the object where this attribute manager is used.
        @param ordered_typing: a list of typing to test/verify and apply when parsing. It is ordered by preference.
        @param is_list: True if the attribute need to be a list.
        @param empty: True if this attribute could be empty.
        @param nullable: True if this attribute could equal to None.
        """
        super().__init__(name, is_list, empty, nullable)
        self._initial_ordered_typing = ordered_typing
        self._ordered_typing = ordered_typing.copy()

        self._set_of_verified_values = set() if unique else None

    def is_unique(self, obj: Any):
        return self._set_of_verified_values is None or obj not in self._set_of_verified_values

    def _verify_unique(self, obj: Any):
        if not self.is_unique(obj):
            raise ValueError(f'{obj} value appearing twice in the item {self._name} (unique constraint).')
        if self._set_of_verified_values is not None:
            self._set_of_verified_values.add(obj)

    def verify(self, obj: Any) -> None:
        """
        Verifies if the current typing strategy corresponds to the object or try the next.
        If there is no next typing strategy, an error is raised.
        @param obj: object to be tested.
        """
        if obj is None:
            if not self._nullable:
                raise TypeError(f'Item {self._name} cannot be None.')
            else:
                return

        self._verify_unique(obj)

        while self._ordered_typing:
            if self._ordered_typing[0].verify(obj):
                return
            self._ordered_typing.pop(0)

        raise TypeError(f'{self._name} has no matching type in {self._initial_ordered_typing} (last unmatching value: "{obj}").')

    def parse(self, obj: Any) -> Any:
        """
        Parses the attribute with the most preferred typing strategy and in accordance with all values tested with attribute manager.
        @param obj: object to be parsed.
        @return: parsed object.
        """
        if obj is None:
            return None
        return self._ordered_typing[0].parse(obj)


class AttributeManagerSet:
    """
    This object is a set of attribute managers needed by a model builder to manage its attributes
    (builders and others for their typing).
    """

    def __init__(self):
        """
        Creates an AttributeManagerSet.
        """
        self._attribute_managers = list()
        self._attribute_managers_by_name = {}

    @property
    def attribute_managers(self):
        """

        @return: the list of attribute managers.
        """
        return self._attribute_managers

    def get_attribute_manager(self, name):
        return self._attribute_managers_by_name[name]

    def add_attribute_manager_for_typing(self, name: str, ordered_typing: List[TypingStrategy], is_list: bool = False,
                                         empty: bool = True,
                                         nullable: bool = True,
                                         unique: bool = False):
        """
        Adds an attribute manager to a given attribute with the order of the different wanted typing in order of
        preference.
        @param name: name of the managed attribute.
        @param ordered_typing: list of ordered typing by preference.
        @param is_list: True if the attribute need to be a list.
        @param empty: True if this attribute could be empty.
        @param nullable: True if this attribute could equal to None.
        @return: the attribute manager with these criteria.
        """
        attr = AttributeManagerForTyping(name, ordered_typing, is_list, empty, nullable, unique)
        self._attribute_managers.append(attr)
        self._attribute_managers_by_name[name] = attr
        return attr

    def add_attribute_manager_for_typing_finder(self, name: str, is_list: bool = False, empty: bool = True,
                                                nullable: bool = True):
        """
        Adds an attribute manager to a given attribute with the order of the different typing in order of
        preference. This list is fixed with this order: integer -> float -> Any.
        @param name: name of the managed attribute.
        @param is_list: True if the attribute need to be a list.
        @param empty: True if this attribute could be empty.
        @param nullable: True if this attribute could equal to None.
        @return: the attribute manager with these criteria.
        """
        return self.add_attribute_manager_for_typing(name, [
            TypingStrategyEnum.INTEGER,
            TypingStrategyEnum.FLOAT,
            TypingStrategyEnum.ANY,
        ], is_list, empty, nullable)

    def add_attribute_manager_for_builder(self, name: str, builder_type: type, is_list: bool = False, empty: bool = True,
                                          nullable: bool = True):
        """
        Adds an attribute manager to a given builder attribute.
        @param name: name of the managed attribute.
        @param builder_type: the type of the builder.
        @param empty: True if this attribute could be empty.
        @param nullable: True if this attribute could equal to None.
        @return: an attribute manager for the builder..
        """
        attr = AttributeManagerForBuilder(name, builder_type, is_list, empty, nullable)
        self._attribute_managers.append(attr)
        self._attribute_managers_by_name[name] = attr
        return attr
