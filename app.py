from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jagdhsflkuaysdfo718349871'

cnx = mysql.connector.connect(
    user = 'hacktuesx',
    password = 'tues10!tues',
    host = 'hacktuesx.mysql.database.azure.com',
    database = 'hacktuesx'
)

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

    #! quiz = generate_multiple_choice_questions()

    quiz = [
        {'question': '1. What is authentication?', 'answers': ['A. The process of giving permission to access a specific resource', 'B. The act of validating that users are whom they claim to be', 'C. An authentication method that enables users to securely authenticate with multiple applications', 'D. The process of generating security codes via an outside party'], 'right_answer': 'B'}, 
        {'question': '2. What is authorization?', 'answers': ['A. The act of validating that users are whom they claim to be', 'B. The process of giving permission to access a specific resource', 'C. An authentication method that enables users to securely authenticate with multiple applications', 'D. The process of generating security codes via an outside party'], 'right_answer': 'B'}, 
        {'question': '3. What is the purpose of multi-factor authentication (MFA)?', 'answers': ['A. To grant access for only one session or transaction', 'B. To generate security codes via an outside party', 'C. To increase security beyond what passwords alone can provide', 'D. To present a fingerprint or eye scan to gain access'], 'right_answer': 'C'}, 
        {'question': '4. Which protocol helps authenticate users and convey information about them?', 'answers': ['A. OAuth 2.0', 'B. OpenID Connect (OIDC)', 'C. SSO', 'D. Biometrics'], 'right_answer': 'B'}, 
        {'question': '5. What does the OAuth 2.0 protocol control?', 'answers': ['A. Authentication', 'B. Authorization', 'C. Single sign-on', 'D. Multi-factor authentication'], 'right_answer': 'B'}, 
        {'question': '6. What is the purpose of SSO?', 'answers': ['A. To grant permission to access a specific resource', 'B. To increase security beyond what passwords alone can provide', 'C. To securely authenticate with multiple applications by using one set of credentials', 'D. To validate that users are whom they claim to be'], 'right_answer': 'C'}, 
        {'question': '7. What is the difference between authentication and authorization?', 'answers': ['A. Authentication confirms users are who they say they are, while authorization gives them permission to access a resource', 'B. Authentication gives permission to access a specific resource, while authorization validates user identities', 'C. Authentication and authorization are the same process', 'D. Authentication and authorization are not related to security'], 'right_answer': 'A'}, 
        {'question': '8. Which method is commonly used for authentication?', 'answers': ['A. Biometrics', 'B. Retrieving and storing authentication information', 'C. Providing administrative access to an application', 'D. Providing permission to download a file on a server'], 'right_answer': 'A'}, 
        {'question': '9. What should always come before authorization in system security?', 'answers': ['A. Multi-factor authentication', 'B. Biometrics', 'C. Authentication', 'D. OAuth 2.0 protocol'], 'right_answer': 'C'}, 
        {'question': '10. How do authentication and authorization work together in a secure environment?', 'answers': ['A. Authentication and authorization are not related', 'B. Authorization is not necessary if authentication is successful', 'C. Users must prove their identities before being granted access to requested resources', 'D. Authorization is always granted before authentication'], 'right_answer': 'C'}
    ]


    # create_quiz(quiz)
    get_all_quizzes()

    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = get_user(request.form['username-field'], request.form['password-field'])
            token = generate_token(user[0])
            return jsonify({'token': jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')}), 200
        except argon2.exceptions.VerifyMismatchError:
            return jsonify({"message": "Invalid username or password"}), 401
    else:
        return render_template("login.html")

@app.route("/quiz/<int:quiz_id>")
def quiz(quiz_id):
    cursor = cnx.cursor()

    cursor.execute("SELECT * FROM quizzes WHERE id = %s", (quiz_id,))
    quiz_row = cursor.fetchone()

    if quiz_row is None:
        return "Quiz not found", 404

    quiz = {
        "id": quiz_row[0],
        "title": quiz_row[1],
        "questions": []
    }

    cursor.execute("SELECT * FROM questions WHERE quiz_id = %s", (quiz_id,))
    question_rows = cursor.fetchall()

    for question_row in question_rows:
        question = {
            "id": question_row[0],
            "question": question_row[2],
            "options": [],
            "correct": None
        }

        cursor.execute("SELECT * FROM answers WHERE question_id = %s", (question["id"],))
        answer_rows = cursor.fetchall()

        for answer_row in answer_rows:
            question["options"].append(answer_row[2])
            if answer_row[3]:
                question["correct"] = answer_row[2]

        quiz["questions"].append(question)

    cursor.close()
    return render_template('quiz.html', quiz=quiz)

def get_all_quizzes():
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM quizzes")
    quizzes = cursor.fetchall()
    print(quizzes)
    cursor.close()

def create_quiz(quiz):
    cursor = cnx.cursor()

    for question in quiz:
        cursor.execute("INSERT INTO quizzes (name) VALUES (%s)", (question['question'],))
        quiz_id = cursor.lastrowid

        cursor.execute("INSERT INTO questions (quiz_id, question_text) VALUES (%s, %s)", (quiz_id, question['question']))
        question_id = cursor.lastrowid

        for option in question['answers']:
            is_correct = (option == question['right_answer'])
            cursor.execute("INSERT INTO answers (question_id, answer_text, is_correct) VALUES (%s, %s, %s)", (question_id, option, is_correct))

    cnx.commit()
    cursor.close()



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


def generate_token(id):
    payload = {
        "id": id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
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
    cnx.close()
