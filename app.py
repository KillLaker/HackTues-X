from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import mysql.connector
import argon2
import jwt
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from jinja2 import Environment, PackageLoader, select_autoescape
from openaiApi import generate_multiple_choice_questions
# from convert_files_to_txt import convert_to_txt
from werkzeug.utils import secure_filename
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jagdhsflkuaysdfo718349871'

@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

@app.route("/upload", methods=['POST'])
def get_uploaded_file():
    try:
        if 'token' not in session:
            return "<h1>User not logged in!</h1>"

        token = session['token']
        json_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')

        if json_token['permission'] != 1:
            return "<h1>Unauthorized access!</h1>"

        uploaded_file = request.files['uploaded-file']

        if 'uploaded-file' not in request.files:
            return render_template('error_uploading.html')

        if len(uploaded_file.filename) == 0:
            return render_template('error_uploading.html')

        app.config['UPLOAD_FOLDER'] = './static/uploads/'


        filename = secure_filename(uploaded_file.filename)

        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], f'quiz-source.{filename.split(".")[-1]}'))

        generate_multiple_choice_questions()
        return redirect(url_for('home'))
    except jwt.exceptions.ExpiredSignatureError:
        return "<h1>Expired session!</h1>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = get_user(request.form['username-field'], request.form['password-field'])

            print(user)

            token = generate_token(user[0], user[3])
            # jsonify({'token': jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')})

            session['token'] = token

            return "<h1>Successfully logged in.</h1>"

        except argon2.exceptions.VerifyMismatchError:
            return jsonify({"message": "Invalid username or password"}), 401
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


def get_user(username, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="user_validator",
        password="user_validator_password",
        database="user-database"
    )

    cursor = conn.cursor()

    cursor.execute("select * from User where username = %s", (username,))
    user = cursor.fetchone()

    print(user)

    if argon2.verify_password(bytes(user[2]), password.encode('utf-8')):
        conn.close()
        return user

    conn.close()
    return None


def generate_token(id, permission):
    payload = {
        "id": id,
        "permission": permission,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=0.016)
    }

    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    form_data = request.form
    selected_options = []
    for key, value in form_data.items():
        if key.startswith('question_'):
            if value:
                selected_options.append(value)

    post_request_text = '\n'.join(selected_options) # Answers only letters
    return 'Quiz submitted!' + post_request_text


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
