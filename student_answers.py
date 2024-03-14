import os
import re

def count_files(directory):
    files = os.listdir(os.path.join(f'{os.path.dirname(__file__)}{directory}'))
    num_files = len(files)
    return num_files

def get_student_answers(directory):
    current_directory = os.path.join(os.path.dirname(__file__), directory)
    answers_2d_array = []
    filename = '01_combined.txt'
    with open(os.path.join(current_directory, filename), 'r') as file:
        first_line = file.readline().strip()
        student_id_match = re.match(r'\d+', first_line)
        if student_id_match:
            student_id = int(student_id_match.group())
            student_answers = []
            for line in file:
                line = line.strip()
                if line.isdigit():
                    # If the line contains a student ID, save the previous student's data
                    answers_2d_array.append([student_id, student_answers])
                    student_id = int(line)
                    student_answers = []
                else:
                    student_answers.append(line)

            if student_id is not None:
                answers_2d_array.append([student_id, student_answers])
    return answers_2d_array

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
                if((filename.split('_')[1].split('.')[0]).isdigit()):
                    student_id = filename.split('_')[1].split('.')[0]
                    print(student_id)
                    combined_file.write(f'{student_id}\n')
                    with open(os.path.join(directory, filename), 'r') as student_file:
                        combined_file.write(student_file.read())

combine_student_answers('Student_answers/')

file_path = "Student_answers"
answers_2d_array = get_student_answers(file_path)
print(answers_2d_array)
#for i, (student_id, answers) in enumerate(answers_2d_array, start=1):
    #print(f"Student {student_id} answers: {answers}")


