from typing import List, Iterable, Dict, Optional

from InquirerPy.validator import EmptyInputValidator

from metrics.scalpel.config import CampaignFormat
from metrics.scalpel.config.wrapper import IScalpelConfigurationWrapper, IDataFileConfigurationWrapper, \
    IRawDataConfigurationWrapper, IFileNameMetaConfigurationWrapper, IInputSetWrapper, \
    DictFileNameMetaConfigurationWrapper, DictRawDataConfigurationWrapper, DictDataFileConfigurationWrapper, \
    EmptyFileNameMetaConfigurationWrapper
from InquirerPy import inquirer


class CLIScalpelConfigurationWrapper(IScalpelConfigurationWrapper):

    def __init__(self):
        self._campaign_path = []

    def get_campaign_name(self) -> Optional[str]:
        return inquirer.text(
            message=f"Campaign name: ",
        ).execute()

    def get_campaign_date(self) -> Optional[str]:
        pass

    def get_os_description(self) -> Optional[str]:
        pass

    def get_cpu_description(self) -> Optional[str]:
        pass

    def get_gpu_description(self) -> Optional[str]:
        pass

    def get_total_memory(self) -> Optional[str]:
        pass

    def get_time_out(self) -> Optional[str]:
        float_val = inquirer.number(
            message="Enter timeout:",
            float_allowed=True,
            validate=EmptyInputValidator(),
        ).execute()

        return float_val

    def get_memory_out(self) -> Optional[str]:
        float_val = inquirer.number(
            message="Enter memout:",
            float_allowed=True,
            validate=EmptyInputValidator(),
        ).execute()

        return float_val

    def get_experiment_wares(self) -> List[Dict[str, str]]:
        return list()

    def get_input_set(self) -> List[IInputSetWrapper]:
        return list()

    def get_campaign_path(self) -> List[str]:
        not_finish = True
        l = []
        while not_finish:
            dest_path = inquirer.filepath(
                message="Enter the campaign path"
            ).execute()
            l.append(dest_path)
            not_finish = inquirer.confirm(message="Add another campaign path?", default=False).execute()
        self._campaign_path = l
        return l

    def get_format(self) -> Optional[str]:
        result = inquirer.select(
            message="Select a campaign format:",
            choices=CampaignFormat.all_yaml_string(),
            default=None,
        ).execute()
        return result

    def has_header(self) -> bool:
        pass

    def get_quote_char(self) -> Optional[str]:
        pass

    def get_separator(self) -> Optional[str]:
        pass

    def get_title_separator(self) -> Optional[str]:
        pass

    def get_follow_symlinks(self) -> bool:
        pass

    def get_custom_parser(self) -> Optional[str]:
        pass

    def get_is_success(self) -> List[str]:
        not_finish = True
        l = []
        while not_finish:
            is_success = inquirer.text(
                message="Is success function (empty for None): ",
                completer={
                    "in": None,
                    "or": None,
                },
                default='',
                multicolumn_complete=True,
            ).execute()
            if is_success == '':
                break
            l.append(is_success)
            not_finish = inquirer.confirm(message="Add another condition?", default=False).execute()
        return l

    def ask_key(self):
        key = inquirer.text(
            message="Key: ",
        ).execute()
        return key

    def ask_value(self):
        value = inquirer.text(
            message="Value: ",
        ).execute()
        return value

    def ask_path(self):
        value = inquirer.text(
            message="Path:",
            completer={v: None for v in self._campaign_path}
        ).execute()
        return value

    def ask_line(self):
        value = inquirer.text(
            message="Line:",
            completer={v: None for v in self._campaign_path}
        ).execute()
        return value

    def get_mapping(self) -> Dict[str, List[str]]:
        not_finish = True
        d = {}
        while not_finish:
            result = inquirer.select(
                message="Type of mapping:",
                choices=["Simple", "Composite", "None"],
                default=None,
            ).execute()
            l = []
            if result == 'None':
                break
            elif result == 'Simple':
                key, value = self.ask_key(), self.ask_value()
                l.append(value)
                d[key] = l
            else:
                another_value = True
                key = self.ask_key()
                while another_value:
                    l.append(self.ask_value())
                    another_value = inquirer.confirm(message="Another value?", default=False).execute()
                d[key] = l
            not_finish = inquirer.confirm(message="Another key?", default=False).execute()
        return d

    def get_default_values(self) -> Dict[str, str]:
        return dict()

    def get_ignored_data(self) -> List[str]:
        return list()

    def get_file_name_meta(self) -> IFileNameMetaConfigurationWrapper:
        if not self.ask_for_add_part("File Name Meta"):
            return EmptyFileNameMetaConfigurationWrapper()
        print("File Name Meta")
        d = dict()
        expression = self.ask_expression()

        file = self.ask_path()
        d[expression] = file

        d['groups'] = dict()

        self.ask_groups(d)
        return DictFileNameMetaConfigurationWrapper(d)

    def ask_groups(self, d):
        print("Start Group")
        not_finish = True
        while not_finish:
            key = self.ask_key()
            group = inquirer.number(
                message=f"Enter group for {key}:",
                validate=EmptyInputValidator(),
            ).execute()
            d['groups'][key] = int(group)
            not_finish = inquirer.confirm(message="Another group?", default=False).execute()
        print("End group")

    def ask_expression(self):
        expression = inquirer.select(
            message="Type of expression:",
            choices=["regex", "pattern"],
            default=None,
        ).execute()
        return expression

    def ask_raw_data(self) -> IRawDataConfigurationWrapper:
        d = dict()
        file = inquirer.text(
            message=f"File: ",
        ).execute()
        expression = self.ask_expression()
        d['file'] = file
        line = self.ask_line()
        d[expression] = line
        d['groups'] = dict()
        self.ask_groups(d)
        return DictRawDataConfigurationWrapper(d)

    def get_raw_data(self) -> Iterable[IRawDataConfigurationWrapper]:
        if not self.ask_for_add_part("Raw Data"):
            return list()
        print("Raw Data")
        list_raw_data = []
        not_finish = True
        while not_finish:
            list_raw_data.append(self.ask_raw_data())
            not_finish = inquirer.confirm(message="Another raw data?", default=False).execute()
        return list_raw_data

    def ask_data_files(self) -> Optional[DictDataFileConfigurationWrapper]:
        path = self.ask_path()
        if path == '':
            return None
        return DictDataFileConfigurationWrapper({'name': path})

    def get_data_files(self) -> Iterable[IDataFileConfigurationWrapper]:
        if not self.ask_for_add_part("Data Files"):
            return list()
        print("Data file")
        list_data_files = []
        not_finish = True
        while not_finish:
            df = self.ask_data_files()
            if df is None:
                break
            list_data_files.append(df)
            not_finish = inquirer.confirm(message="Another raw data?", default=False).execute()
        return list_data_files

    def ask_for_add_part(self, message):
        return inquirer.confirm(message=f"Do you want add {message}?", default=False).execute()

    def get_ignored_files(self) -> List[str]:
        pass
