import os

def count_files(directory):
    files = os.listdir(directory)
    num_files = len(files)
    return num_files

import os

def get_student_answers(directory):
    os.chdir(directory)
    rows = sum(1 for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename)) and filename != "correct_answers.txt")
    answers = []
    for filename in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, filename)) or filename == "correct_answers.txt":
            continue
        student_answers = []
        with open(os.path.join(directory, filename), 'r') as f:
            for line in f:
                student_answers.append(line.strip())
        answers.append(student_answers)
    return answers

