import os

def read_correct_answers(directory):
    #directory = 'D:/HackTues-X/Student_answers/'
    filename = 'correct_answers.txt'
    answers = []
    with open(os.path.join(directory, filename), 'r') as f:
        for line in f:
            answers.append(line.strip())
    return answers

