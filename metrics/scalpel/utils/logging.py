###############################################################################
#                                                                             #
#  Scalpel - A Metrics Module                                                 #
#  Copyright (c) 2019-2022- Univ Artois & CNRS, Exakis Nelite                 #
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
This module provides logging tools to trace the extraction performed by Scalpel,
mostly for debugging purposes (for instance, to identify why some data is missing
for a particular experiment).
"""


from sys import stderr
from time import time
from typing import Callable

from loguru import logger


class LevelFilter:
    """
    The LevelFilter allows deciding whether a record is to be logged.
    """

    def __init__(self, level: str) -> None:
        """
        Creates a new LevelFilter.

        :param level: The minimum level for the records to log.
        """
        self.level = level

    def __call__(self, record) -> bool:
        """
        Checks whether the given record is to be logged.

        :param record: The record to check.

        :return: Whether the record is to be logged.
        """
        level_no = logger.level(self.level).no
        return record['level'].no >= level_no


def timeit(func: Callable) -> Callable:
    """
    Wraps a function to measure and log the execution time of this function.

    :param func: The function to wrap.

    :return: The wrapped function.
    """
    def wrapped(*args, **kwargs):
        logger.info(f'entering {func.__name__}')
        start = time()
        result = func(*args, **kwargs)
        end = time()
        logger.info('exiting {} executed in {:f} seconds', func.__name__, end - start)
        return result
    return wrapped


def configure_logger(level: str) -> None:
    """
    Configures the logger to be used by Scalpel.

    :param level: The minimum level for the records to log.
    """
    logger.remove()
    level_filter = LevelFilter(level)
    logger.add(stderr, filter=level_filter, level=0)
