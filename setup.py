###############################################################################
#                                                                             #
#  Metrics - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                #
#  -------------------------------------------------------------------------- #
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
Setup script for deploying Metrics on PyPI and allowing to install it using pip.
"""

from setuptools import setup

import metrics


def readme() -> str:
    """
    Reads the README file of the project to use it as long description.

    :return: The long description of Metrics.
    """
    with open('README.md') as file:
        return file.read()


setup(
    name='crillab-metrics',
    version=metrics.__version__,
    packages=[
        'metrics.core',
        'metrics.scalpel',
        'metrics.scalpel.config',
        'metrics.scalpel.parser',
        'metrics.wallet',
        'metrics.wallet.dataframe',
        'metrics.wallet.figure',
        'metrics.studio.web',
        'metrics'
    ],

    description=metrics.__summary__,
    long_description=readme(),
    long_description_content_type='text/markdown',
    keywords=metrics.__keywords__,
    install_requires=[
        "Brotli==1.0.7",
        "cachelib==0.1.1",
        "certifi==2019.11.28",
        "chardet==3.0.4",
        "click==7.1.2",
        "coverage==5.1",
        "cycler==0.10.0",
        "dash==1.13.4",
        "dash-bootstrap-components==0.10.3",
        "dash-core-components==1.10.1",
        "dash-html-components==1.0.3",
        "dash-renderer==1.5.1",
        "dash-table==4.8.1",
        "Flask==1.1.2",
        "Flask-Caching==1.9.0",
        "Flask-Compress==1.5.0",
        "Flask-Session==0.3.2",
        "future==0.18.2",
        "gunicorn==20.0.4",
        "idna==2.9",
        "importlib-metadata==1.7.0",
        "itsdangerous==1.1.0",
        "Jinja2==2.11.2",
        "jsonpickle==1.4.1",
        "kiwisolver==1.1.0",
        "MarkupSafe==1.1.1",
        "matplotlib==3.2.0",
        "numpy==1.18.1",
        "pandas==1.0.1",
        "plotly==4.5.4",
        "prompt-toolkit==1.0.14",
        "pyfiglet==0.8.post1",
        "Pygments==2.6.1",
        "PyInquirer==1.0.3",
        "pyparsing==2.4.6",
        "python-dateutil==2.8.1",
        "pytz==2019.3",
        "PyYAML==5.3",
        "regex==2020.2.20",
        "requests==2.23.0",
        "retrying==1.3.3",
        "six==1.14.0",
        "urllib3==1.25.8",
        "wcwidth==0.1.8",
        "Werkzeug==1.0.1",
        "wrapt==1.12.1",
        "zipp==3.1.0"

    ],

    author=metrics.__author__,
    author_email=metrics.__email__,
    url=metrics.__uri__,

    test_suite='nose.collector',
    tests_require=['nose'],

    scripts=[
        'bin/metrics-cli',
        'bin/metrics-scalpel',
    ],

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent'
    ],
    license=metrics.__license__,

    include_package_data=True,
    zip_safe=False
)
