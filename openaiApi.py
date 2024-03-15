from openai import OpenAI
from dotenv import load_dotenv
import os
from flask import request


def generate_multiple_choice_questions():
    load_dotenv()

    api_key = os.getenv("API_KEY")

    client = OpenAI(api_key=api_key)

    quiz_source = open("static/uploads/quiz-source.txt", "r", encoding="utf-8")
    file_text = quiz_source.read()
    # questions_number = request.form['questions-number']
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "user",
                "content": "Generate 10 multiple-choice questions with 4 choices and only one correct based on the given information. " + file_text + "\n The language of the question must match the input information language (Български, English). After each question, include the correct answer in the format ': X' after all question choices, where X is the correct letter and only the capital letter.  Please ensure that the questions are clear, concise, and directly related to the provided information. Use a variety of question types (e.g., factual, inferential) to enhance the diversity of the quiz. Remember to maintain consistency in formatting and grammar throughout the questions and answers."

# "file_text + "\ngenerate 10 multiple choice questions based on the information given above and after every question print the right answer like this Answer: X"
            }
        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    response_content = response.choices[0].message.content
    questions = []
    current_question = ""
    current_answers = []
    current_right_answer = ""

    for line in response_content.split("\n"):
        line = line.strip()
        if line.endswith("?"):
            if current_question:
                question_dict = {
                    "question": current_question,
                    "answers": current_answers,
                    "right_answer": current_right_answer
                }
                questions.append(question_dict)
                current_answers = []
                current_right_answer = ""
            current_question = line
        elif line.startswith(("a)", "b)", "c)", "d)", "A.", "B.", "C.", "D.")) or line.startswith(
                ("A)", "B)", "C)", "D)")):
            current_answers.append(line)

        elif line.startswith(": ") or line.startswith("Answer:") or line.startswith("Отговор:") or line.startswith("Right answer: ") or line.startswith("Правилен отговор: "):
            current_right_answer = line.split(":")[1].strip()

    if current_question:
        question_dict = {
            "question": current_question,
            "answers": current_answers,
            "right_answer": current_right_answer
        }
        questions.append(question_dict)

    for question in questions:
        print("Question:", question["question"])
        print("Answers:", question["answers"])
        print("Right answer:", question["right_answer"])

    print(response_content)

    return questions

# generate_multiple_choice_questions()

