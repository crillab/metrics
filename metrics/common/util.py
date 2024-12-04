# from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
import os
import re
from datetime import timedelta

import loguru
from git import Repo
from platformdirs import user_data_dir

import metrics
from metrics.studio.constant import METRICS_DIR_CONFIG

UNITS_TIME = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}


def convert_to_seconds(text):
    """
        Convert a string representing a duration (e.g., "1h", "30m", "2.5d") into an integer representing the total time in seconds.

        Args:
            text (str): The input string containing numerical values followed by optional time units.
                        Supported units are:
                        - 's' for seconds
                        - 'm' for minutes
                        - 'h' for hours
                        - 'd' for days
                        - 'w' for weeks
                        If no unit is provided, the value is assumed to be in seconds.

        Returns:
            int: The equivalent duration in seconds.

        Example:
            convert_to_seconds("1h") -> 3600
            convert_to_seconds("30m") -> 1800
            convert_to_seconds("2.5d") -> 216000
            convert_to_seconds("45s") -> 45
            convert_to_seconds("3w") -> 1814400
            convert_to_seconds("120") -> 120
        """
    return int(timedelta(**{
        UNITS_TIME.get(m.group('unit').lower(), 'seconds'): float(m.group('val'))
        for m in re.finditer(
            r'(?P<val>\d+(\.\d+)?)(?P<unit>[smhdw]?)',
            text.replace(' ', ''),
            flags=re.I
        )
    }).total_seconds())


UNITS_SIZE = {
    'kb': 1 / 1024,
    'mb': 1,
    'gb': 1024,
    'tb': 1024 * 1024
}


def convert_to_megabytes(text):
    """
    Convert a string representing a file size (e.g., "1GB", "1024MB") into an integer representing the size in megabytes.

    Args:
        text (str): The input string containing a numerical value followed by an optional unit (KB, MB, GB, TB).
                    If no unit is provided, the value is assumed to be in megabytes.

    Returns:
        int: The equivalent size in megabytes.

    Example:
        convert_to_megabytes("1GB") -> 1024
        convert_to_megabytes("1024MB") -> 1024
        convert_to_megabytes("500KB") -> 0
        convert_to_megabytes("1TB") -> 1048576
        convert_to_megabytes("500") -> 500
    """
    match = re.match(r'(?P<val>\d+(\.\d+)?)(?P<unit>[kmgbt]b?)?', text.strip().lower())
    if not match:
        raise ValueError("Invalid format")

    value = float(match.group('val'))
    unit = match.group('unit') or 'mb'

    return int(value * UNITS_SIZE.get(unit, 1))


def get_cache_dir() -> str:
    appname = metrics.__title__.lower()
    appauthor = metrics.__title__.lower()
    cache_dir = user_data_dir(appname, appauthor)
    return cache_dir


def get_cache_ew_config_file():
    return os.path.join(get_cache_dir(), METRICS_DIR_CONFIG, "ew.yaml")


def get_cache_ew_cache_file():
    return os.path.join(get_cache_ew_dir(), ".ew_cache.yaml")


def get_cache_ew_dir():
    return os.path.join(get_cache_dir(), "cache", "experiment-ware")


def walk_through_files(path, file_extensions):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if len(file_extensions) == 0:
                yield os.path.join(dirpath, filename)
            for extension in file_extensions:
                if filename.endswith(extension):
                    yield os.path.join(dirpath, filename)


def create_cache_directory():
    cache_dir = get_cache_dir()
    loguru.logger.info(f"Creating cache directory: {cache_dir}")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(os.path.join(cache_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(cache_dir, "config"), exist_ok=True)
    os.makedirs(os.path.join(cache_dir, "cache"), exist_ok=True)
    os.makedirs(os.path.join(cache_dir, "cache", "xcsp"), exist_ok=True)
    os.makedirs(os.path.join(cache_dir, "cache", "mzn"), exist_ok=True)
    os.makedirs(os.path.join(cache_dir, "cache", "experiment-ware"), exist_ok=True)


def download_metadata():
    loguru.logger.info("Downloading or updating xcsp metadata...")
    xcsp_cache = os.path.join(get_cache_dir(), "cache", "xcsp")
    metadata_dir = os.path.join(xcsp_cache, "metadata")
    if not os.path.exists(metadata_dir):
        cloned_repo = Repo.clone_from("https://github.com/thibaultfalque/xcsp3-metadata",
                                      metadata_dir)
    else:
        cloned_repo = Repo(metadata_dir)
    cloned_repo.remote().pull()


def unknown_command(args):
    loguru.logger.error("Unknown command.")


class ChangeDirectory:
    def __init__(self, new_path):
        self.new_path = new_path
        self.saved_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)
