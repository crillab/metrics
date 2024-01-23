# from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
import os
from datetime import timedelta
import re

from platformdirs import user_data_dir

import metrics

UNITS = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}


def convert_to_seconds(text):
    return int(timedelta(**{
        UNITS.get(m.group('unit').lower(), 'seconds'): float(m.group('val'))
        for m in re.finditer(
            r'(?P<val>\d+(\.\d+)?)(?P<unit>[smhdw]?)',
            text.replace(' ', ''),
            flags=re.I
        )
    }).total_seconds())


def get_cache_dir() -> str:
    appname = metrics.__title__.lower()
    appauthor = metrics.__title__.lower()
    cache_dir = user_data_dir(appname, appauthor)
    return cache_dir


def walk_through_files(path, file_extensions):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            for extension in file_extensions:
                if filename.endswith(extension):
                    yield os.path.join(dirpath, filename)
