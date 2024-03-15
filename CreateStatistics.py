import matplotlib.pyplot as plt
from tkinter import *
import numpy as np

import student_answers as s_a
import correct_answers as c_a
import os


def answers_fidelity(correctAnswersCount, IncorrectAnswersCount, save_path, i, student_id):
    if correctAnswersCount == 0:
        sizes = np.array([IncorrectAnswersCount])
        labels = ['Incorrect']
    elif IncorrectAnswersCount == 0:
        sizes = np.array([correctAnswersCount])
        labels = ['Correct']
    else:
        sizes = np.array([correctAnswersCount, IncorrectAnswersCount])
        labels = ['Correct', 'Incorrect']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title(f"Answers Fidelity {student_id}. number")

    plt.savefig(save_path)
    plt.close()

def statistics(inputData, save_path, i):
    plt.suptitle(f'Question {i}', fontsize=18)
    plt.hist(inputData, bins=len(inputData) * 2, alpha=0.7, edgecolor='black')
    plt.yticks(np.arange(0, len(inputData) + 1, 1))
    plt.savefig(save_path)  
    plt.close()

def check_question_answers(question_answers, correct_answers):
    correct = 0
    incorrect = 0
    print(question_answers, correct_answers)
    for correct_answer, student_answer in zip(correct_answers, question_answers):
        print(student_answer, correct_answer, correct, incorrect)
        if student_answer == correct_answer:
            correct += 1
        else:
            incorrect += 1
    return correct, incorrect
def create_diagram():
    root = Tk()
    root.title("Test statistics")
    root.iconbitmap('statistics.png')
    root.geometry('800x400')

    save_statistics_directory = 'Statistics'

    save_diagrams_directory = '/Diagrams'

    answer_directory = '/Student_answers/correct_answers'

    #answers = s_a.get_student_answers(answer_directory)
    correct_answers = c_a.read_correct_answers(answer_directory)
    #print('corrrr', correct_answers)


    student_answers = s_a.get_student_answers('Student_answers')
    for i, (student_id, answers) in enumerate(student_answers, start=1):
        save_path_statistics = os.path.dirname(__file__) + f'/Statistics/statistic_{i}.png'
        statistics(answers, save_path_statistics, i)
        correct_count, incorrect_count = check_question_answers(answers, correct_answers)
        save_path_diagrams = os.path.dirname(__file__) + f'/Diagrams/diagrams_{student_id}.png'
        print('aaa', correct_count, incorrect_count)
        answers_fidelity(correct_count, incorrect_count, save_path_diagrams, i, student_id)

    # for i, question_answers in enumerate(zip(*answers)):
    #
    #     correct_count, incorrect_count = check_question_answers(question_answers, correct_answers[i])
    #     print(f"Question {i+1}: Correct: {correct_count}, Incorrect: {incorrect_count}")
    #
    #     statistics(question_answers, save_path_statistics, i)
    #
    #
    #
    #
    print("Histograms saved successfully!")