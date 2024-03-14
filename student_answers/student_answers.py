import os

def count_files():
    files = os.listdir(os.getcwd())
    num_files = len(files)
    return num_files

def get_student_answers():
    rows = count_files() - 1
    cols = 5
    student_indx = 0
    answers = [[0 for _ in range(cols)] for _ in range(rows)]
    for filename in os.listdir(os.getcwd()):
        if filename == "student_answers.py":
            continue
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            for i, line in enumerate(f):
                answers[student_indx][i] = line.strip()
            student_indx += 1

    return answers

def __main__():


__main__()
