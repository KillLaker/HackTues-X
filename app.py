from flask import Flask, render_template, request, redirect, url_for, flash
from jinja2 import Environment, PackageLoader, select_autoescape
from openaiApi import generate_multiple_choice_questions
# from convert_files_to_txt import convert_to_txt
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

@app.route("/upload", methods=['POST'])
def get_uploaded_file():
    uploaded_file = request.files['uploaded-file']

    if 'uploaded-file' not in request.files:
        return render_template('error_uploading.html')

    if len(uploaded_file.filename) == 0:
        return render_template('error_uploading.html')

    app.config['UPLOAD_FOLDER'] = './static/uploads/'
    # convert_to_txt(uploaded_file)
    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'quiz-source.txt'))

    generate_multiple_choice_questions()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass
    else:
        return render_template("login.html")
@app.route("/quiz/<int:quiz>")
def quiz(quiz):

    # Read the data from the database 

    quiz = {
        "id": quiz,
        "title": "Quiz 1",
        "questions": [
            {
                "id": 1,
                "question": "What is the capital of France?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "correct": "Paris"
            },
            {
                "id": 2,
                "question": "What is the capital of Germany?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "correct": "Berlin"
            },
            {
                "id": 3,
                "question": "What is the capital of Spain?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "correct": "Madrid"
            },
            {
                "id": 4,
                "question": "What is the capital of United Kingdom?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "correct": "London"
            }
        ]
    }

    return render_template('quiz.html', quiz=quiz)

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    form_data = request.form
    selected_options = []
    for key, value in form_data.items():
        if key.startswith('question_'):
            if value:
                selected_options.append(value)

    post_request_text = '\n'.join(selected_options) # Answers only letters

    filename = f'D:/HackTues-X/Student_answers/student_{quiz_id}.txt'
    with open(filename, 'w') as f:
        f.write(post_request_text)
    return 'Quiz submitted! Answers saved in ' + filename

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)