import os

def count_files(directory):
    files = os.listdir(os.path.join(f'{os.path.dirname(__file__)}{directory}'))
    num_files = len(files)
    return num_files

import os

def get_student_answers(directory):

    current_directory = os.path.join(f'{os.path.dirname(__file__)}{directory}')
    #print(current_directory)
    #rint(directory)
    os.chdir(current_directory)
    rows = sum(1 for filename in os.listdir(current_directory) if os.path.isfile(current_directory + filename) and filename != "correct_answers.txt")
    answers = []

    for filename in os.listdir(current_directory):

        path = directory + filename
        if os.path.isdir(path) or filename == "correct_answers.txt" or filename == "__pycache__":
            continue
        student_answers = []
        print(current_directory + '/' + filename)
        with open((current_directory + '/' + filename), 'r', encoding='utf-8') as f:
            for line in f:
                student_answers.append(line.strip())

        answers.append(student_answers)
        print(answers)
    return answers


