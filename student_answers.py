import os
import re

def count_files(directory):
    files = os.listdir(os.path.join(f'{os.path.dirname(__file__)}{directory}'))
    num_files = len(files)
    return num_files

def get_student_answers(directory, quiz_id):
    current_directory = os.path.join(os.path.dirname(__file__), directory)
    answers_2d_array = []
    filename = f'{quiz_id}_combined.txt'
    with open(os.path.join(current_directory, filename), 'r') as file:
        first_line = file.readline().strip()
        student_id_match = re.match(r'\d+', first_line)
        if student_id_match:
            student_id = int(student_id_match.group())
            student_answers = []
            for line in file:
                line = line.strip()
                if line.isdigit():
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
        if filename.endswith('.txt') and filename != '1_combined.txt':
            parts = filename.split('_')
            if len(parts) == 2:
                quiz_id, student_id = parts
                quiz_files.setdefault(quiz_id, []).append(filename)

    for quiz_id, files in quiz_files.items():
        combined_filename = f'{quiz_id}_combined.txt'
        with open(os.path.join(directory, combined_filename), 'w') as combined_file:
            for filename in files:
                student_id = filename.split('_')[1].split('.')[0]
                combined_file.write(f'{student_id}\n')  # Write student ID
                with open(os.path.join(directory, filename), 'r') as student_file:
                    combined_file.write(student_file.read().strip() + '\n')  # Write student answers
                print(f'Added answers for student {student_id} from file {filename}')
        print(f'Combined answers for quiz {quiz_id} into file {combined_filename}')

#combine_student_answers('Student_answers/')


#file_path = "Student_answers"
#answers_2d_array = get_student_answers(file_path, quiz_id=1)
#print(answers_2d_array)
#for i, (student_id, answers) in enumerate(answers_2d_array, start=1):
    #print(f"Student {student_id} answers: {answers}")


