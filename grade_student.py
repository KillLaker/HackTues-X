def calculate_grade(selected_options, answers):
    grade = 0
    total_questions = len(answers)
    for user_answer, correct_answer in zip(selected_options, answers):
        if user_answer == correct_answer:
            grade += 1

    percentage_grade = grade / total_questions

    return round(percentage_grade, 2)