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
    # print(question_answers, correct_answers)
    for correct_answer, student_answer in zip(correct_answers, question_answers):
        print(student_answer, correct_answer, correct, incorrect)
        if student_answer == correct_answer:
            correct += 1
        else:
            incorrect += 1
    return correct, incorrect


def count_answers(data, num_questions):
    answer_counts = [{} for _ in range(num_questions)]
    for _, answers in data:
        for i, answer in enumerate(answers):
            answer_counts[i][answer] = answer_counts[i].get(answer, 0) + 1
    return answer_counts


def create_statistics(quiz_id):
    root = Tk()
    root.title("Test statistics")
    root.iconbitmap('statistics.png')
    root.geometry('800x400')

    answer_directory = f'/Student_answers/correct_answers/{quiz_id}_correct_answers'
    correct_answers = c_a.read_correct_answers(answer_directory)

    student_answers = s_a.get_student_answers('Student_answers', quiz_id)
    number_of_questions = len(student_answers[0][1])
    number_of_answers = count_answers(student_answers, number_of_questions)
    print(number_of_answers)

    answerrs = count_answers(student_answers, number_of_questions)

    with open(os.path.join(os.path.dirname(__file__), 'Student_answers', 'correct_answers',
                           f'{quiz_id}_correct_answers.txt')) as correct_answers_file:
        correct_answers_content = correct_answers_file.readlines()

        # Assume correct answers are in the same order as the questions
    correct_answers = [answer.strip() for answer in correct_answers_content]
    # print("aaa", student_answers)
    for i, (student_id, answers) in enumerate(student_answers, start=1):
        correct_count, incorrect_count = check_question_answers(answers, correct_answers)
        save_path_diagrams = os.path.dirname(__file__) + f'/static/Diagrams/diagrams_{student_id}.png'
        answers_fidelity(correct_count, incorrect_count, save_path_diagrams, i, student_id)

    for i, counts in enumerate(answerrs, start=1):
        labels = list(counts.keys())
        values = list(counts.values())


        plt.figure(figsize=(8, 6))
        plt.bar(labels, values, color=['blue', 'orange', 'green', 'red'])
        plt.title(f'Question {i} Answer Distribution')
        plt.xlabel('Answers')
        plt.ylabel('Count')

        save_path_statistics = os.path.dirname(__file__) + f'/static//Statistics'
        if not os.path.exists(save_path_statistics):
            os.makedirs(save_path_statistics)

        save_path = os.path.join(save_path_statistics, f'statistic_q{i}.png')
        plt.savefig(save_path)
        plt.close()
        print(f'Saved histogram for Question {i} at: {save_path}')

#test
# create_statistics('1')
# print("Histograms saved successfully!")

