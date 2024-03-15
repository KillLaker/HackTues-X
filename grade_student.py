def calculate_grade(selected_options, answers):
    grade = 0
    total_questions = len(answers)
    for user_answer, correct_answer in zip(selected_options, answers):
        if user_answer == correct_answer:
            grade += 1

    percentage_grade = grade / total_questions

    return round(percentage_grade, 2)


def get_wrong_questions(selected_options, answers):
    wrong_questions = []
    question_id = 1
    for user_answer, correct_answer in zip(selected_options, answers):
        if user_answer == correct_answer:
            wrong_questions.append([question_id, "correct"])
        else:
            wrong_questions.append([question_id, "incorrect"])
        question_id += 1
    return wrong_questions
