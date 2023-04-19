

from __future__ import print_function, unicode_literals

from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint


class Main():

    def __init__(self):
        
        style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: '',
        })
        print("Welcome to the Anonymizer! Please answer the following questions to get started. (Press Ctrl+C to exit at any time.)")

        questions = [
            {
                'type': 'list',
                'message': 'What type of database do you want to anonymize?',
                'name': 'database_type',
                'choices': [
                    {
                        'name': 'Use my own database (in CSV format)'
                    },
                    {
                        'name': 'Generate a random database'
                    },
                ],
                'validate': lambda answer: 'You must choose at least a type.' \
                    if len(answer) == 0 else True
            }
        ]
        answers = prompt(questions, style=style)
        pprint(answers)

main = Main()
