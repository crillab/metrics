# ##############################################################################
#                                                                              #
#  Studio (CLI) - A Metrics Module
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                 #
#  --------------------------------------------------------------------------  #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity  #
#  sTUdIO - inTerface for bUilding experIment repOrts                          #
#                                                                              #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify it     #
#  under the terms of the GNU Lesser General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or (at your  #
#  option) any later version.                                                  #
#                                                                              #
#  This program is distributed in the hope that it will be useful, but         #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY  #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                        #
#  See the GNU General Public License for more details.                        #
#                                                                              #
#  You should have received a copy of the GNU Lesser General Public License    #
#  along with this program.                                                    #
#  If not, see <https://www.gnu.org/licenses/>.                                #
#                                                                              #
# ##############################################################################
from typing import Any

from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError
from regex import regex


class NumberValidator(Validator):
    def validate(self, document):
        ok = regex.match(r'^(?P<min>\d+),(?P<max>\d+)$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid number',
                cursor_position=len(document.text))  # Move cursor to end
        groups = ok.groupdict()
        if int(groups["min"]) > int(groups["max"]):
            raise ValidationError(
                message='Min must be inferior to max.',
                cursor_position=len(document.text))


def minimum_one_choice_validator(document):
    print(document)
    if len(document) == 0:
        raise ValidationError(message='You must choose at least one element')
    return True


class InteractiveMode:
    """
        This class is used for create an interactive mode with the user for gets the plot configuration.
    """

    def __init__(self, builder):
        self._plot_questions = {
            'Cactus Plot': self._prompt_cactus_questions, 'Scatter plot': self._prompt_scatter_questions,
            'Box plot': ""
        }
        self._builder = builder
        self._base_questions = {}

    def create_question(self) -> 'InteractiveMode':
        """
            This method create the questions for users.
        """
        self._base_questions = [
            {
                'type': 'checkbox',
                'qmark': '\N{bar chart}',
                'message': 'Select plots',
                'name': 'plots',
                'choices': [

                    {
                        'name': v
                    } for v in self._plot_questions.keys()
                ],
                'validate': minimum_one_choice_validator
            }
        ]
        return self

    def _get_common_question(self, prefix):
        return [
            {
                'type': "input",
                'message': 'Please enter a title',
                'name': f'{prefix}_title'
            },
            {
                'type': 'checkbox',
                'qmark': '\N{fire}',
                'message': 'Please choose solver to compare',
                'name': f'{prefix}_solver_choice',
                'choices': [
                    {
                        'name': v
                    } for v in ["s1", "s2", "s3"]
                ],
                'validate': minimum_one_choice_validator
            },
            {
                'type': 'confirm',
                'message': 'Do you want log scale? (default=No)',
                'name': f'{prefix}_log',
                'default': False,
            },
            {
                'type': 'confirm',
                'message': 'Do you want specify limits of chart? (default=No)',
                'name': f'{prefix}_limits',
                'default': False,
            },
            {
                'type': 'input',
                'message': 'Enter the limits (min,max): ',
                'name': f'{prefix}_limits_min_max',
                'when': lambda answer: answer[f'{prefix}_limits'],
                'validate': NumberValidator
            },
        ]

    def _prompt_cactus_questions(self):
        print("################ Cactus Plot ################")
        answers = prompt(self._get_common_question("cactus") + [
            {
                'type': 'confirm',
                'qmark': '\N{family}',
                'message': 'Do you want a cactus by family? (default=No)',
                'name': 'cactus_family',
                'default': False,

            },
            {
                'type': 'checkbox',
                'qmark': '\N{family}',
                'message': 'Please choose family',
                'when': lambda answer: answer['cactus_family'],
                'name': 'cactus_family_choice',
                'choices': [
                    {
                        'name': v
                    } for v in ["family1", "family2", "family3"]
                ],
                'validate': minimum_one_choice_validator
            }
        ])

    def _prompt_scatter_questions(self):
        print("################ Scatter Plot ################")
        answers = prompt(self._get_common_question("scatter") + [
            {
                'type': 'confirm',
                'message': 'Do you want differentiate family? (default=No)',
                'default': False,
                'name': 'scatter_family'
            },
            {
                'type': 'confirm',
                'message': 'Do you want create a scatter by decision? (default=No)',
                'default': False,
                'name': 'scatter_decision'
            }
        ])

    def _prompt_questions_from_base_answers(self, answers):
        for p in answers["plots"]:
            self._plot_questions[p]()

    def prompt(self) -> Any:
        """
        This method prompts the user question and gets the answers.
        @return: The answers of users
        """
        answers = prompt(self._base_questions)
        self._prompt_questions_from_base_answers(answers)
        return self._builder
