import matplotlib.pyplot as plt
from tkinter import *
import numpy as np

import student_answers as s_a
import correct_answers as c_a
import os


def answers_fidelity(correctAnswersCount, IncorrectAnswersCount, save_path, i):
    # Filter out zero values
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
    plt.title(f"Answers Fidelity {i + 1}")

    # Save the plot
    plt.savefig(save_path)
    plt.close()

def statistics(inputData, save_path, i):
    plt.suptitle(f'Question {i + 1}', fontsize=18)
    plt.hist(inputData, bins=len(inputData) * 2, alpha=0.7, edgecolor='black')
    plt.yticks(np.arange(0, len(inputData) + 1, 1))
    plt.savefig(save_path)  # Save the histogram as a PNG file
    plt.close()

def check_question_answers(question_answers, correct_answers):
    correct = 0
    incorrect = 0
    print(correct_answers)
    for correct_answer in correct_answers:
        for student_answer in question_answers:
            if student_answer == correct_answer:
                correct += 1
            else:
                incorrect += 1
    return correct, incorrect

if __name__ == '__main__':
    root = Tk()
    root.title("Test statistics")
    root.iconbitmap('statistics.png')
    root.geometry('800x400')

    # Save directory for the statistics
    save_statistics_directory = 'Statistics'

    save_diagrams_directory = '/Diagrams'

    # Specify the directory containing student answer files
    answer_directory = '/Student_answers'

    # Read student answers and correct answers
    answers = s_a.get_student_answers(answer_directory)
    correct_answers = c_a.read_correct_answers(answer_directory)

    #print(answers)



    # Iterate over each question
    for i, question_answers in enumerate(zip(*answers)):

        correct_count, incorrect_count = check_question_answers(question_answers, correct_answers[i])
        print(f"Question {i+1}: Correct: {correct_count}, Incorrect: {incorrect_count}")


        save_path_statistics = os.path.dirname(__file__) + f'/Statistics/statistic_{i}.png'
        statistics(question_answers, save_path_statistics, i)

        save_path_diagrams = os.path.dirname(__file__) + f'/Diagrams/diagrams_{i}.png'

        answers_fidelity(correct_count, incorrect_count, save_path_diagrams, i)
    print("Histograms saved successfully!")
