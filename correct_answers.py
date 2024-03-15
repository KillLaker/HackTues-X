import os

def read_correct_answers(directory, quiz_id):
    filename = f"{quiz_id}_correct_answers.txt"
    dir = os.path.dirname(__file__)
    dir = dir.replace('\\', '/')
    current_directory = os.path.join(f"{dir}{directory}.txt")
    answers = []
    with open(os.path.join(current_directory), 'r') as f:
        for line in f:
            answers.append(line.strip())
    return answers

#read_correct_answers("/Student_answers/correct_answers/1_correct_answers")

