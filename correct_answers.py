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

def combine_student_answers(directory):
    filenames = os.listdir(directory)
    quiz_files = {}

    for filename in filenames:
        if filename.endswith('.txt'):
            quiz_id, student_id = filename.split('_')
            quiz_files.setdefault(quiz_id, []).append(filename)

    for quiz_id, files in quiz_files.items():
        combined_filename = f'{quiz_id}_combined.txt'
        with open(os.path.join(directory, combined_filename), 'w') as combined_file:
            for filename in files:
                student_id = filename.split('_')[1].split('.')[0]
                combined_file.write(f'user id: {student_id}\n')
                with open(os.path.join(directory, filename), 'r') as student_file:
                    combined_file.write(student_file.read())
                combined_file.write('\n---\n')

combine_student_answers('Student_answers/')