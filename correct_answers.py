import os

def read_correct_answers(directory):
    #directory = 'D:/HackTues-X/Student_answers/'
    filename = 'correct_answers.txt'
    current_directory = os.path.join(f"{os.path.dirname(__file__)}{directory}")
    os.chdir(current_directory)
    answers = []
    with open(os.path.join(current_directory, filename), 'r') as f:
        for line in f:
            answers.append(line.strip())
    return answers

