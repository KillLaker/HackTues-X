from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

client = OpenAI(api_key=api_key)

quiz_source = open("static/uploads/quiz-source.txt", "r")
file_text = quiz_source.read()

response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
        {
            "role": "user",
            "content": file_text + "\ngenerate 10 multiple choice questions based on the information given above на български"
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

for line in response_content.split("\n"):
    line = line.strip()
    if line.endswith("?"):
        if current_question:
            question_dict = {
                "question": current_question,
                "answers": current_answers
            }
            questions.append(question_dict)
            current_answers = []
        current_question = line
    elif line.startswith(("a)", "b)", "c)", "d)")):
        current_answers.append(line)

if current_question:
    question_dict = {
        "question": current_question,
        "answers": current_answers
    }
    questions.append(question_dict)


for question in questions:
    print("Question:", question["question"])
    print("Answers:", question["answers"])
    print()

# print(response_content)
