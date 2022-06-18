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
This module provides a common interface for the different ways of configuring
Scalpel by defining wrappers for them.
"""


from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from metrics.core.constants import XP_WARE_NAME


class IInputSetWrapper:
    """
    The IInputSetWrapper defines a wrapper interface for the different ways of
    describing the input-sets used in a campaign.
    """

    def get_name(self) -> str:
        """
        Gives the name of the input-set.

        :return: The name of the input-set.
        """
        raise NotImplementedError('Method "get_name()" is abstract!')

    def get_type(self) -> str:
        """
        Gives the type of the input-set.

        :return: The type of the input-set.
        """
        raise NotImplementedError('Method "get_type()" is abstract!')

    def get_extensions(self) -> List[str]:
        """
        Gives the extensions of the files of the input-set.

        :return: The list of the extensions.
        """
        raise NotImplementedError('Method "get_extensions()" is abstract!')

    def get_file_name_meta(self) -> IFileNameMetaConfigurationWrapper:
        """
        Gives the description of the metadata to extract from the name of the
        files in the input-set.

        :return: The description of the metadata.
        """
        raise NotImplementedError('Method "get_file_name_meta()" is abstract!')

    def get_files(self) -> List[Any]:
        """
        Gives the description of the files of the input-set.

        :return: The description of the files.
        """
        raise NotImplementedError('Method "get_files()" is abstract!')


class IFileNameMetaConfigurationWrapper:
    """
    The IFileNameMetaConfigurationWrapper defines a wrapper interface for the
    different ways of configuring the extraction of metadata from file names.
    """

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern describing how to extract metadata from
        the name of a file.

        :return: The simplified pattern for extracting metadata.
        """
        raise NotImplementedError('Method "get_simplified_pattern()" is abstract!')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression describing how to extract metadata from
        the name of a file.

        :return: The regular expression for extracting metadata.
        """
        raise NotImplementedError('Method "get_regex_pattern()" is abstract!')

    def get_groups(self) -> Iterable[Tuple[str, int]]:
        """
        Gives the relevant groups of the pattern describing how to extract
        metadata from the name of a file.

        :return: The names and indices of the relevant groups.
        """
        raise NotImplementedError('Method "get_groups()" is abstract!')

    def is_exact(self) -> bool:
        """
        Checks whether the pattern for the name of the file must match exactly
        this name.

        :return: Whether the pattern is exact.
        """
        raise NotImplementedError('Method "is_exact()" is abstract!')


class IRawDataConfigurationWrapper:
    """
    The IRawDataConfigurationWrapper defines a wrapper interface for the
    different ways of configuring raw data to extract from campaign files.
    """

    def get_file(self) -> str:
        """
        Gives the file from which to extract the raw data.

        :return: The file containing the raw data.
        """
        raise NotImplementedError('Method "get_file()" is abstract!')

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern describing the raw data.

        :return: The simplified pattern for the raw data, if any.
        """
        raise NotImplementedError('Method "get_simplified_pattern()" is abstract!')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression describing the raw data.

        :return: The regular expression for the raw data, if any.
        """
        raise NotImplementedError('Method "get_regex_pattern()" is abstract!')

    def get_groups(self) -> Iterable[Tuple[str, int]]:
        """
        Gives the relevant groups of the pattern describing how to extract
        the raw-data.

        :return: The names and indices of the relevant groups.
        """
        raise NotImplementedError('Method "get_groups()" is abstract!')

    def is_exact(self) -> bool:
        """
        Checks whether the pattern must match exactly the parsed lines.

        :return: Whether the pattern is exact.
        """
        raise NotImplementedError('Method "is_exact()" is abstract!')


class IDataFileConfigurationWrapper:
    """
    The IDataFileConfigurationWrapper defines a wrapper interface for the
    different ways of configuring data-files produced by a campaign.
    """

    def get_name(self) -> str:
        """
        Gives the name of the data-file.

        :return: The name of the data-file
        """
        raise NotImplementedError('Method "get_name()" is abstract!')

    def has_name_as_prefix(self) -> bool:
        """
        Checks whether the name of the data-file must be used as a prefix to
        distinguish the content of this file from that of others.

        :return: Whether the name of this file must be used as prefix.
        """
        raise NotImplementedError('Method "has_name_as_prefix()" is abstract!')

    def get_format(self) -> Optional[str]:
        """
        Gives the format of the data-file.

        :return: The format of the data-file (if specified).
        """
        raise NotImplementedError('Method "get_format()" is abstract!')

    def has_header(self) -> bool:
        """
        Checks whether the data-file has a header.

        :return: If the data-file has a header.
        """
        raise NotImplementedError('Method "has_header()" is abstract!')

    def get_quote_char(self) -> Optional[str]:
        """
        Gives the quote character used to escape special characters in the data-file.

        :return: The quote character that is used (if specified).
        """
        raise NotImplementedError('Method "get_quote_char()" is abstract!')

    def get_separator(self) -> Optional[str]:
        """
        Gives the separator used to distinguish different fields in the data-file.

        :return: The separator that is used (if specified).
        """
        raise NotImplementedError('Method "get_separator()" is abstract!')

    def get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) name of the class of the custom parser to use
        to parse the data-file.

        :return: The class of the parser to use (if specified).
        """
        raise NotImplementedError('Method "get_custom_parser()" is abstract!')


class IScalpelConfigurationWrapper:
    """
    The IScalpelConfigurationWrapper defines a wrapper interface for the
    different ways of configuring Scalpel.
    """

    def get_campaign_name(self) -> Optional[str]:
        """
        Gives the name of the campaign being considered.

        :return: The name of the campaign (if specified).
        """
        raise NotImplementedError('Method "get_campaign_name()" is abstract!')

    def get_campaign_date(self) -> Optional[str]:
        """
        Gives the date of the campaign being considered.

        :return: The date of the campaign (if specified).
        """
        raise NotImplementedError('Method "get_campaign_date()" is abstract!')

    def get_os_description(self) -> Optional[str]:
        """
        Gives the description of the operating system on which the campaign has
        been executed.

        :return: The description of the OS (if specified).
        """
        raise NotImplementedError('Method "get_os_description()" is abstract!')

    def get_cpu_description(self) -> Optional[str]:
        """
        Gives the description of the CPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the CPU (if specified).
        """
        raise NotImplementedError('Method "get_cpu_description()" is abstract!')

    def get_gpu_description(self) -> Optional[str]:
        """
        Gives the description of the GPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the GPU (if specified).
        """
        raise NotImplementedError('Method "get_gpu_description()" is abstract!')

    def get_total_memory(self) -> Optional[str]:
        """
        Gives the total amount of memory available on the machine(s) on which the
        campaign has been executed.

        :return: The total amount of memory (if specified).
        """
        raise NotImplementedError('Method "get_total_memory()" is abstract!')

    def get_time_out(self) -> Optional[str]:
        """
        Gives the time limit set to the experiments in this campaign.

        :return: The configured time limit (if specified).
        """
        raise NotImplementedError('Method "get_time_out()" is abstract!')

    def get_memory_out(self) -> Optional[str]:
        """
        Gives the memory limit set to the experiments in this campaign.

        :return: The configured memory limit (if specified).
        """
        raise NotImplementedError('Method "get_memory_out()" is abstract!')

    def get_experiment_wares(self) -> List[Dict[str, str]]:
        """
        Gives the description of the experiment-wares that have been executed
        in the campaign that is being parsed.

        :return: The description of the experiment-wares.
        """
        raise NotImplementedError('Method "get_experiment_wares()" is abstract!')

    def get_input_set(self) -> List[IInputSetWrapper]:
        """
        Gives the description of the inputs that have been used for the campaign.

        :return: The description of the inputs.
        """
        raise NotImplementedError('Method "get_input_set()" is abstract!')

    def get_campaign_path(self) -> List[str]:
        """
        Gives the path of the files containing all the data about the campaign.
        These files may be either regular files or directories.

        :return: The path to the main files of the campaign.
        """
        raise NotImplementedError('Method "get_campaign_path()" is abstract!')

    def get_format(self) -> Optional[str]:
        """
        Gives the format of the campaign to parse.

        :return: The format of the campaign to parse (if specified).
        """
        raise NotImplementedError('Method "get_format()" is abstract!')

    def has_header(self) -> bool:
        """
        Checks whether the input files to parse have a header.

        :return: If the input files to parse have a header.
        """
        raise NotImplementedError('Method "has_header()" is abstract!')

    def get_quote_char(self) -> Optional[str]:
        """
        Gives the quote character used to escape special characters in the files to parse.

        :return: The quote character that is used (if specified).
        """
        raise NotImplementedError('Method "get_quote_char()" is abstract!')

    def get_separator(self) -> Optional[str]:
        """
        Gives the separator used to distinguish different fields in the files to parse.

        :return: The separator that is used (if specified).
        """
        raise NotImplementedError('Method "get_separator()" is abstract!')

    def get_title_separator(self) -> Optional[str]:
        """
        Gives the separator used to distinguish different elements in the titles of
        the files to parse.

        :return: The title separator that is used (if specified).
        """
        raise NotImplementedError('Method "get_title_separator()" is abstract!')

    def get_follow_symlinks(self) -> bool:
        """
        Checks whether symbolic links should be followed when exploring a file hierarchy.

        :return: Whether symlinks should be followed.
        """
        raise NotImplementedError('Method "get_follow_symlinks()" is abstract!')

    def get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) name of the class of the custom parser to use
        to parse the campaign.

        :return: The class of the parser to use (if specified).
        """
        raise NotImplementedError('Method "get_custom_parser()" is abstract!')

    def get_is_success(self) -> List[str]:
        """
        Gives the list of the expressions to evaluate to determine whether an experiment
        is successful.

        :return: The list of expressions to evaluate.
        """
        raise NotImplementedError('Method "get_is_success()" is abstract!')

    def get_mapping(self) -> Dict[str, List[str]]:
        """
        Gives the dictionary defining the mapping allowing to retrieve the data
        expected by Scalpel from the experiment files.

        :return: The specified mapping.
        """
        raise NotImplementedError('Method "get_mapping()" is abstract!')

    def get_default_values(self) -> Dict[str, str]:
        """
        Gives the default values to consider when a value is missing for an experiment.

        :return: The dictionary associating some Scalpel keys to the corresponding
                 default values.
        """
        raise NotImplementedError('Method "get_default_values()" is abstract!')

    def get_ignored_data(self) -> List[str]:
        """
        Gives the data that should be ignored when read by Scalpel.

        :return: The list of the keys identifying the data to ignore.
        """
        raise NotImplementedError('Method "get_ignored_data()" is abstract!')

    def get_file_name_meta(self) -> IFileNameMetaConfigurationWrapper:
        """
        Gives the description of the metadata to extract from the name of the
        files of the campaign.

        :return: The description of the metadata.
        """
        raise NotImplementedError('Method "get_file_name_meta()" is abstract!')

    def get_raw_data(self) -> Iterable[IRawDataConfigurationWrapper]:
        """
        Gives the raw data configuration, which describes how to extract data
        from the log files of the experiment-wares.
        Such data is only meaningful when the campaign is stored in a directory.

        :return: The raw data configuration.
        """
        raise NotImplementedError('Method "get_raw_data()" is abstract!')

    def get_data_files(self) -> Iterable[IDataFileConfigurationWrapper]:
        """
        Gives the description of the data files to consider for each experiment,
        which must be in a format that Scalpel natively recognizes (JSON, CSV, etc.).
        Such files are only meaningful when the campaign is stored in a "deep"
        file hierarchy.

        :return: The list of data files.
        """
        raise NotImplementedError('Method "get_data_files()" is abstract!')

    def get_ignored_files(self) -> List[str]:
        """
        Gives the files that should not be parsed by Scalpel.

        :return: The files to ignore.
        """
        raise NotImplementedError('Method "get_ignored_files()" is abstract!')


class DictInputSetWrapper(IInputSetWrapper):
    """
    The DictInputSetWrapper defines a wrapper for an input-set that is described
    using a dictionary-like structure.
    """

    def __init__(self, dict_config: Dict[str, Any]) -> None:
        """
        Creates a new DictInputSetWrapper.

        :param dict_config: The configuration of the input-set.
        """
        self._dict_config = dict_config

    def get_name(self) -> str:
        """
        Gives the name of the input-set.

        :return: The name of the input-set.
        """
        return self._dict_config['name']

    def get_type(self) -> str:
        """
        Gives the type of the input-set.

        :return: The type of the input-set.
        """
        return self._dict_config['type']

    def get_extensions(self) -> List[str]:
        """
        Gives the extensions of the files of the input-set.

        :return: The list of the extensions.
        """
        return _as_list(self._dict_config.get('extensions'))

    def get_file_name_meta(self) -> IFileNameMetaConfigurationWrapper:
        """
        Gives the description of the metadata to extract from the name of the
        files in the input-set.

        :return: The description of the metadata.
        """
        file_name_meta = self._dict_config.get('file-name-meta')
        if file_name_meta is None:
            return EmptyFileNameMetaConfigurationWrapper()
        return DictFileNameMetaConfigurationWrapper(file_name_meta)

    def get_files(self) -> List[Dict[str, Any]]:
        """
        Gives the description of the files of the input-set.

        :return: The description of the files.
        """
        files = self._dict_config.get('files')
        return _as_list(files)


class EmptyFileNameMetaConfigurationWrapper(IFileNameMetaConfigurationWrapper):
    """
    The EmptyFileNameMetaConfigurationWrapper defines a wrapper for a filename
    metadata configuration that does not exist.
    """

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern describing how to extract metadata from
        the name of a file.

        :return: Always None.
        """
        return None

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression describing how to extract metadata from
        the name of a file.

        :return: Always None.
        """
        return None

    def get_groups(self) -> Iterable[Tuple[str, int]]:
        """
        Gives the relevant groups of the pattern describing how to extract
        metadata from the name of a file.

        :return: Always an empty list.
        """
        return []

    def is_exact(self) -> bool:
        """
        Checks whether the pattern for the name of the file must match exactly
        this name.

        :return: Always False.
        """
        return False


class DictFileNameMetaConfigurationWrapper(IFileNameMetaConfigurationWrapper):
    """
    The DictFileNameMetaConfigurationWrapper defines a wrapper for a filename
    metadata configuration defined with a dictionary-like structure.
    """

    def __init__(self, dict_config: Dict[str, Any]) -> None:
        """
        Creates a new DictFileNameMetaConfigurationWrapper.

        :param dict_config: The configuration of the filename metadata.
        """
        self._dict_config = dict_config

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern describing how to extract metadata from
        the name of a file.

        :return: The simplified pattern for extracting metadata.
        """
        return self._dict_config.get('pattern')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression describing how to extract metadata from
        the name of a file.

        :return: The regular expression for extracting metadata.
        """
        return self._dict_config.get('regex')

    def get_groups(self) -> Iterable[Tuple[str, int]]:
        """
        Gives the relevant groups of the pattern describing how to extract
        metadata from the name of a file.

        :return: The names and indices of the relevant groups.
        """
        groups = self._dict_config.get('groups')
        return groups.items()

    def is_exact(self) -> bool:
        """
        Checks whether the pattern for the name of the file must match exactly
        this name.

        :return: Whether the pattern is exact.
        """
        exact = self._dict_config.get('exact')
        return _as_boolean(exact, default=False)


class DictRawDataConfigurationWrapper(IRawDataConfigurationWrapper):
    """
    The DictRawDataConfigurationWrapper defines a wrapper for a pattern
    describing raw-data with a dictionary-like structure.
    """

    def __init__(self, dict_config: Dict[str, Any]) -> None:
        """
        Creates a new DictRawDataConfigurationWrapper.

        :param dict_config: The configuration for raw-data.
        """
        self._dict_config = dict_config

    def get_file(self) -> str:
        """
        Gives the file from which to extract the raw data.

        :return: The file containing the raw data.
        """
        return self._dict_config['file']

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern describing the raw data.

        :return: The simplified pattern for the raw data, if any.
        """
        return self._dict_config.get('pattern')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression describing the raw data.

        :return: The regular expression for the raw data, if any.
        """
        return self._dict_config.get('regex')

    def get_groups(self) -> Iterable[Tuple[str, int]]:
        """
        Gives the relevant groups of the pattern describing how to extract
        the raw-data.

        :return: The names and indices of the relevant groups.
        """
        groups = self._dict_config.get('groups')
        if isinstance(groups, dict):
            # The groups already associate a name to its group index.
            return groups.items()

        # Looking for the names of the groups.
        names = self._dict_config.get('log-data')
        if not names:
            names = self._dict_config.get('name')

        # (Legacy) mapping between identifiers and indices.
        identifiers = _as_list(names)
        indices = _as_list(groups, [1])
        if len(identifiers) == 1 and len(indices) > 1:
            identifier = identifiers[0]
            identifiers = [f'{identifier}{i}' for i in range(len(indices))]
        return zip(identifiers, indices)

    def is_exact(self) -> bool:
        """
        Checks whether the pattern must match exactly the parsed lines.

        :return: Whether the pattern is exact.
        """
        exact = self._dict_config.get('exact')
        return _as_boolean(exact, default=False)


class DictDataFileConfigurationWrapper(IDataFileConfigurationWrapper):
    """
    The IDataFileConfigurationWrapper defines a wrapper interface for the
    configuration of a data-file defined with a dictionary-like structure.
    """

    def __init__(self, dict_config: Dict[str, Any]) -> None:
        """
        Creates a new DictDataFileConfigurationWrapper.

        :param dict_config: The configuration of the data-file.
        """
        self._dict_config = dict_config

    def get_name(self) -> str:
        """
        Gives the name of the data-file.

        :return: The name of the data-file
        """
        return self._dict_config['name']

    def has_name_as_prefix(self) -> bool:
        """
        Checks whether the name of the data-file must be used as a prefix to
        distinguish the content of this file from that of others.

        :return: Whether the name of this file must be used as prefix.
        """
        prefix = self._dict_config.get('name-as-prefix')
        return _as_boolean(prefix)

    def get_format(self) -> Optional[str]:
        """
        Gives the format of the data-file.

        :return: The format of the data-file (if specified).
        """
        return self._dict_config.get('format')

    def has_header(self) -> bool:
        """
        Checks whether the data-file has a header.

        :return: If the data-file has a header.
        """
        header = self._dict_config.get('has-header')
        return _as_boolean(header, default=True)

    def get_quote_char(self) -> Optional[str]:
        """
        Gives the quote character used to escape special characters in the data-file.

        :return: The quote character that is used (if specified).
        """
        return self._dict_config.get('quote-char')

    def get_separator(self) -> Optional[str]:
        """
        Gives the separator used to distinguish different fields in the data-file.

        :return: The separator that is used (if specified).
        """
        return self._dict_config.get('separator')

    def get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) name of the class of the custom parser to use
        to parse the data-file.

        :return: The class of the parser to use (if specified).
        """
        return self._dict_config.get('parser')


class DictScalpelConfigurationWrapper(IScalpelConfigurationWrapper):
    """
    The DictScalpelConfigurationWrapper defines a wrapper for a configuration
    of Scalpel defined with a dictionary-like structure.
    """

    def __init__(self, dict_config: Dict[str, Any]) -> None:
        """
        Creates a new DictScalpelConfigurationWrapper.

        :param dict_config: The configuration of Scalpel.
        """
        self._dict_config = dict_config

    def get_campaign_name(self) -> Optional[str]:
        """
        Gives the name of the campaign being considered.

        :return: The name of the campaign (if specified).
        """
        return self._dict_config.get('name')

    def get_campaign_date(self) -> Optional[str]:
        """
        Gives the date of the campaign being considered.

        :return: The date of the campaign (if specified).
        """
        return self._dict_config.get('date')

    def get_os_description(self) -> Optional[str]:
        """
        Gives the description of the operating system on which the campaign has
        been executed.

        :return: The description of the OS (if specified).
        """
        return self._get_dict('setup').get('os')

    def get_cpu_description(self) -> Optional[str]:
        """
        Gives the description of the CPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the CPU (if specified).
        """
        return self._get_dict('setup').get('cpu')

    def get_gpu_description(self) -> Optional[str]:
        """
        Gives the description of the GPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the GPU (if specified).
        """
        return self._get_dict('setup').get('gpu')

    def get_total_memory(self) -> Optional[str]:
        """
        Gives the total amount of memory available on the machine(s) on which the
        campaign has been executed.

        :return: The total amount of memory (if specified).
        """
        return self._get_dict('setup').get('ram')

    def get_time_out(self) -> Optional[str]:
        """
        Gives the time limit set to the experiments in this campaign.

        :return: The configured time limit (if specified).
        """
        return self._get_dict('setup').get('timeout')

    def get_memory_out(self) -> Optional[str]:
        """
        Gives the memory limit set to the experiments in this campaign.

        :return: The configured memory limit (if specified).
        """
        return self._get_dict('setup').get('memout')

    def get_experiment_wares(self) -> List[Dict[str, str]]:
        """
        Gives the description of the experiment-wares that have been executed
        in the campaign that is being parsed.

        :return: The description of the experiment-wares.
        """
        xp_wares = self._dict_config.get('experiment-wares')
        return _collect_descriptions(XP_WARE_NAME, xp_wares)

    def get_input_set(self) -> List[IInputSetWrapper]:
        """
        Gives the description of the input-sets that have been used for the campaign.

        :return: The description of the input-sets.
        """
        given_input_sets = self._dict_config.get('input-set')
        input_sets = _as_list(given_input_sets)
        return [DictInputSetWrapper(i) for i in input_sets]

    def get_campaign_path(self) -> List[str]:
        """
        Gives the path of the files containing all the data about the campaign.
        These files may be either regular files or directories.

        :return: The path to the main files of the campaign.
        """
        path = self._get_dict('source').get('path')
        return _as_list(path)

    def get_format(self) -> Optional[str]:
        """
        Gives the format of the campaign to parse.

        :return: The format of the campaign to parse (if specified).
        """
        return self._get_dict('source').get('format')

    def has_header(self) -> bool:
        """
        Checks whether the input files to parse have a header.

        :return: If the input files to parse have a header.
        """
        header = self._get_dict('source').get('has-header')
        return _as_boolean(header, default=True)

    def get_quote_char(self) -> Optional[str]:
        """
        Gives the quote character used to escape special characters in the files to parse.

        :return: The quote character that is used (if specified).
        """
        return self._get_dict('source').get('quote-char')

    def get_separator(self) -> Optional[str]:
        """
        Gives the separator used to distinguish different fields in the files to parse.

        :return: The separator that is used (if specified).
        """
        return self._get_dict('source').get('separator')

    def get_title_separator(self) -> Optional[str]:
        """
        Gives the separator used to distinguish different elements in the titles of
        the files to parse.

        :return: The title separator that is used (if specified).
        """
        return self._get_dict('source').get('title-separator')

    def get_follow_symlinks(self) -> bool:
        """
        Checks whether symbolic links should be followed when exploring a file hierarchy.

        :return: Whether symlinks should be followed.
        """
        follow = self._get_dict('source').get('follow-symlinks')
        return _as_boolean(follow, default=False)

    def get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) name of the class of the custom parser to use
        to parse the campaign.

        :return: The class of the parser to use (if specified).
        """
        return self._get_dict('source').get('parser')

    def get_is_success(self) -> List[str]:
        """
        Gives the list of the expressions to evaluate to determine whether an experiment
        is successful.

        :return: The list of expressions to evaluate.
        """
        is_success = self._get_dict('source').get('is-success')
        return _as_list(is_success)

    def get_mapping(self) -> Dict[str, List[str]]:
        """
        Gives the dictionary defining the mapping allowing to retrieve the data
        expected by Scalpel from the experiment files.

        :return: The specified mapping.
        """
        # Checking whether there is a mapping.
        mapping = self._get_dict('data').get('mapping')
        if mapping is None:
            return {}

        # Normalizing the mapping.
        normalized_mapping = {}
        for key, value in mapping.items():
            normalized_mapping[key] = _as_list(value)
        return normalized_mapping

    def get_default_values(self) -> Dict[str, str]:
        """
        Gives the default values to consider when a value is missing for an experiment.

        :return: The dictionary associating some Scalpel keys to the corresponding default values.
        """
        default_values = self._get_dict('data').get('default-values')
        if default_values is None:
            return {}
        return default_values

    def get_ignored_data(self) -> List[str]:
        """
        Gives the data that should be ignored when read by Scalpel.

        :return: The list of the keys identifying the data to ignore.
        """
        ignored_data = self._get_dict('data').get('ignored-data')
        return _as_list(ignored_data)

    def get_file_name_meta(self) -> IFileNameMetaConfigurationWrapper:
        """
        Gives the description of the metadata to extract from the name of the
        files of the campaign.

        :return: The description of the metadata.
        """
        file_name_meta = self._get_dict('data').get('file-name-meta')
        if file_name_meta is None:
            return EmptyFileNameMetaConfigurationWrapper()
        return DictFileNameMetaConfigurationWrapper(file_name_meta)

    def get_raw_data(self) -> List[IRawDataConfigurationWrapper]:
        """
        Gives the raw data configuration, which describes how to extract data
        from the log files of the experiment-wares.
        Such data is only meaningful when the campaign is stored in a directory.

        :return: The raw data configuration.
        """
        raw_data = self._get_dict('data').get('raw-data')
        raw_data_list = _as_list(raw_data)
        return [DictRawDataConfigurationWrapper(d) for d in raw_data_list]

    def get_data_files(self) -> List[IDataFileConfigurationWrapper]:
        """
        Gives the description of the data files to consider for each experiment,
        which must be in a format that Scalpel natively recognizes (JSON, CSV, etc.).
        Such files are only meaningful when the campaign is stored in a "deep"
        file hierarchy.

        :return: The list of data files.
        """
        given_data_files = self._get_dict('data').get('data-files')
        descriptions = _collect_descriptions('name', given_data_files)
        return [DictDataFileConfigurationWrapper(d) for d in descriptions]

    def get_ignored_files(self) -> List[str]:
        """
        Gives the files that should not be parsed by Scalpel.

        :return: The files to ignore.
        """
        ignored_files = self._get_dict('data').get('ignored-files')
        return _as_list(ignored_files)

    def _get_dict(self, key: str) -> Dict[str, Any]:
        """
        Gives the dictionary containing the configuration for the specified key.

        :return: The configuration for the specified key, or an empty dictionary
                 if the configuration is not specified.
        """
        value = self._dict_config.get(key)
        if value is None:
            return {}
        return value


def _collect_descriptions(identifier: str, descriptions: Any) -> List[Dict[str, str]]:
    """
    Creates a list of descriptions for the elements of the campaign having the given
    identifier.

    :param identifier: The key identifying the elements.
    :param descriptions: The descriptions of the elements.

    :return: The collected descriptions.
    """
    description_list = _as_list(descriptions)
    return [_build_description(identifier, d) for d in description_list]


def _build_description(identifier: str, description: Any) -> Dict[str, str]:
    """
    Creates a dictionary representing the given description of an element of
    the campaign.

    :param identifier: The key identifying the element.
    :param description: The description of the element.

    :return: The dictionary describing the element.
    """
    if isinstance(description, dict):
        return description
    return {identifier: description}


def _as_boolean(obj: Any, default: bool = False) -> bool:
    """
    Represents an object as a Boolean value.

    :param obj: The object to represent as a Boolean value.
    :param default: The default Boolean value for the object.

    :return: The boolean interpretation of the object.
    """
    if obj is None:
        return default
    if isinstance(obj, bool):
        return obj
    return bool(obj)


def _as_list(obj: Any, default: Iterable[Any] = tuple()) -> List[Any]:
    """
    Represents an object as a list of values.

    :param obj: The object to represent as a list.
    :param default: The default list representation for the object.

    :return: The list representation of the object.
    """
    if obj is None:
        return list(default)
    if isinstance(obj, list):
        return obj
    return [obj]
