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
This module provides a convenient way to read the input-set(s) used in a
campaign from different formats.
"""


from os import path, sep, walk
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Union

from metrics.core.constants import INPUT_NAME
from metrics.scalpel.config.format import InputSetFormat
from metrics.scalpel.listener import CampaignParserListener


class InputSetReader:
    """
    The InputSetReader is the base class for reading the description of an
    input set used for a campaign.
    """

    def __init__(self, listener: CampaignParserListener) -> None:
        """
        Creates a new InputSetReader.

        :param listener: The listener to notify about the read input set.
        """
        self._listener = listener

    def read(self) -> None:
        """
        Reads the description of the different inputs of the input set.
        """
        raise NotImplementedError('Method "read()" is abstract!')

    def _start_input(self) -> None:
        """
        Notifies the listener that a new input description is being read.
        """
        self._listener.start_input()

    def _log_data(self, key: str, value: Any) -> None:
        """
        Notifies the listener about data that has been read about an input.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        self._listener.log_data(key, value)

    def _end_input(self) -> None:
        """
        Notifies the listener that the description of the current input has
        been fully read.
        """
        self._listener.end_input()


class ListInputSetReader(InputSetReader):
    """
    The ListInputSetReader reads an input set from a list containing dictionaries
    representing the inputs of this input set.
    """

    def __init__(self, listener: CampaignParserListener,
                 input_set: List[Dict[str, Any]], extensions, file_name_meta) -> None:
        """
        Creates a new ListInputSetReader.

        :param listener: The listener to notify about the read input set.
        :param input_set: The description of the input set, as a list of inputs
                          (dictionaries).
        """
        super().__init__(listener)
        self._input_set = input_set
        self._file_name_meta = file_name_meta
        self._extensions = extensions

    def read(self):
        """
        Reads the description of the different inputs of the input set.
        """
        for input_description in self._input_set:
            self._start_input()
            file = input_description[INPUT_NAME]
            if self._is_ignored(file):
                continue
            for k, v in self._file_name_meta.extract_from(file).items():
                self._log_data(k, v)
            for key, value in input_description.items():
                self._log_data(key, value)
            self._end_input()

    def _is_ignored(self, file: str) -> bool:
        """
        Checks whether the given file is ignored while exploring the file hierarchy.

        :param file: The file to check.

        :return: If the file is ignored.
        """
        if self._extensions is None:
            # All files are considered.
            return False

        # Checking if the file has one of the expected extensions.
        for ext in self._extensions:
            if file.endswith(ext):
                return False
        return True


class FileListInputSetReader(InputSetReader):
    """
    The FileListInputSetReader reads an input set from the list of the files
    contained in the input set.
    """

    def __init__(self, listener: CampaignParserListener, files: Iterable[str],
                 extensions, file_name_meta):
        """
        Creates a new FileListInputSetReader.

        :param listener: The listener to notify about the read input set.
        :param files: The files contained in the input set.
        :param family: The family of the inputs to read.
                       If a string is given, its value is used as the name of
                       the family.
                       If an integer is given, its value is used as a position
                       in the path of the files.
                       If None is given, no family is considered for the read inputs.
        :param name: The position in the path of the files that identify the name
                     of an input.
        :param extensions: The list of the extensions of the files to be considered as
                           input files.
        """
        super().__init__(listener)
        self._file_list = files
        self._file_name_meta = file_name_meta
        self._extensions = extensions

    def read(self) -> None:
        """
        Reads the files of the input set, and extracts their description.
        """
        for file in self._file_list:
            self._start_input()
            self._extract_data(file.strip())
            self._end_input()

    def _extract_data(self, file: str) -> None:
        """
        Extracts the description of an input, given by its path.

        :param file: The path of the input file to extract the description of.
        """
        if self._is_ignored(file):
            return

        # Considering the file.
        self._log_data(INPUT_NAME, file)

        # Retrieving the name of the input.
        for k, v in self._file_name_meta.extract_from(file).items():
            self._log_data(k, v)

    def _is_ignored(self, file: str) -> bool:
        """
        Checks whether the given file is ignored while exploring the file hierarchy.

        :param file: The file to check.

        :return: If the file is ignored.
        """
        if self._extensions is None:
            # All files are considered.
            return False

        # Checking if the file has one of the expected extensions.
        for ext in self._extensions:
            if file.endswith(ext):
                return False
        return True


class HierarchyInputSetReader:
    """
    The HierarchyInputSetReader reads a set of inputs by exploring the file
    hierarchy containing these inputs.
    """

    def __init__(self, listener: CampaignParserListener, root_dir: str,
                 extensions, file_name_meta):
        """
        Creates a new HierarchyInputSetReader.

        :param listener: The listener to notify about the read input set.
        :param root_dir: The root directory of the file hierarchy to explore.
        :param family: The family of the inputs to read.
                       If a string is given, its value is used as the name of
                       the family.
                       If an integer is given, its value is used as a position
                       in the path of the files.
                       If None is given, no family is considered for the read inputs.
        :param name: The position in the path of the files that identify the name
                     of an input.
        :param extensions: The list of the extensions of the files to be considered as
                           input files.
        """
        self._listener = listener
        self._root_dir = root_dir
        self._file_name_meta = file_name_meta
        self._extensions = extensions

    def read(self) -> None:
        """
        Reads the files of the input set, and extracts their description.
        """
        reader = FileListInputSetReader(self._listener, self._walk(),
                                        self._extensions, self._file_name_meta)
        reader.read()

    def _walk(self) -> Generator[str, None, None]:
        """
        Walks the file hierarchy rooted at the associated directory.

        :return: A generator of all files contained in the hierarchy.
        """
        for directory, _, files in walk(self._root_dir):
            for file in files:
                yield path.join(directory, file)


def create_input_set_reader(fmt: InputSetFormat, extensions, file_name_meta) -> Callable[[CampaignParserListener, Any], None]:
    """
    Creates a reader for an input-set in the given format.

    :param fmt: The format of the input-set to read.

    :return: The function to use to read the input-set.
    """
    if fmt == InputSetFormat.LIST:
        return lambda l, s: _str_reader(ListInputSetReader, l, s, extensions, file_name_meta)

    if fmt == InputSetFormat.FILE_LIST:
        return lambda l, s: _str_reader(FileListInputSetReader, l, s, extensions, file_name_meta)

    if fmt == InputSetFormat.FILE:
        return lambda l, s: _file_reader(l, s[0], extensions, file_name_meta)

    return lambda l, s: _str_reader(HierarchyInputSetReader, l, s[0], extensions, file_name_meta)


def _str_reader(factory: Callable, listener: CampaignParserListener, source: Any, extensions, file_name_meta) -> None:
    """
    Reads an input-set from a list containing the description of the inputs.

    :param factory: The function to call to create the appropriate reader.
    :param listener: The listener to notify while reading.
    :param source: The source from which to read the input.
    """
    reader = factory(listener, source, extensions, file_name_meta)
    reader.read()


def _file_reader(listener: CampaignParserListener, source: Any, extensions, file_name_meta):
    """
    Reads an input-set from a file containing the list of the inputs to consider.

    :param listener: The listener to notify while reading.
    :param source: The source from which to read the input.
    """
    with open(source, 'r') as file:
        reader = FileListInputSetReader(listener, file, extensions, file_name_meta)
        reader.read()
