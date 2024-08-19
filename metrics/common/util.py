# from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
import os
import re
from datetime import timedelta

import loguru
from git import Repo
from platformdirs import user_data_dir

import metrics
from metrics.studio.constant import METRICS_DIR_CONFIG

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


def get_cache_ew_config_file():
    return os.path.join(get_cache_dir(), METRICS_DIR_CONFIG, "ew.yaml")


def get_cache_ew_cache_file():
    return os.path.join(get_cache_ew_dir(), ".ew_cache.yaml")


def get_cache_ew_dir():
    return os.path.join(get_cache_dir(), "cache", "experiment-ware")


def walk_through_files(path, file_extensions):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
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
