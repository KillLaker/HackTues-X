import matplotlib.pyplot as plt
from tkinter import *
import student_answers as s_a


def statistics(inputData, save_path):
    plt.hist(inputData, bins=len(inputData)*2)
    plt.savefig(save_path)  # Save the histogram as PNG file
    plt.close()


if __name__ == '__main__':
    # the page which is opened when running the program
    root = Tk()
    root.title("Test statistics")
    root.iconbitmap('D:/statistics.png')
    root.geometry('800x400')

    # Save directory for the statistics
    save_directory = 'D:/HackTues-X/Statistics/'

    # Specify the directory containing student answer files
    answer_directory = 'D:/HackTues-X/Student_answers'

    answers = s_a.get_student_answers(answer_directory)

    # Iterate over each row in the 2D array
    questions = [[] for _ in range(5)]  # 5 is the number of questions
    for row in answers:
        for col_index, element in enumerate(row):
            questions[col_index].append(element)
            #print(questions[col_index])


    for i, question in enumerate(questions):
        print(question)
        save_path = save_directory + f'statistic_{i}.png'
        statistics(question, save_path)

    print("Histograms saved successfully!")
