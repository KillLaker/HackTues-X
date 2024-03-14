import os

def count_files(directory):
    files = os.listdir(directory)
    num_files = len(files)
    return num_files

def get_student_answers(directory):
    os.chdir(directory)
    rows = count_files(directory) - 1
    cols = 5
    student_indx = 0
    answers = [[0 for _ in range(cols)] for _ in range(rows)]
    for filename in os.listdir(directory):
        # Skip directories
        if os.path.isdir(os.path.join(directory, filename)):
            continue
        if filename == "student_answers.py":
            continue
        with open(os.path.join(directory, filename), 'r') as f:
            for i, line in enumerate(f):
                answers[student_indx][i] = line.strip()
            student_indx += 1

    return answers
