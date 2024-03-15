from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import mysql.connector
import argon2
import jwt
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from jinja2 import Environment, PackageLoader, select_autoescape
from openaiApi import generate_multiple_choice_questions
from openai import OpenAI
from werkzeug.utils import secure_filename
from convert_files_to_txt import *
from dotenv import load_dotenv
import os

load_dotenv()
cnx = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME')
)
 
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route("/", methods=['GET'])
def home():
    try:
        if 'token' not in session:
            flash("Either no account detected or session expired!")
            return redirect(url_for('login'))

        return render_template('index.html', is_logged_in=session.get('token', False))
    except jwt.exceptions.ExpiredSignatureError:
        flash("Either no account detected or session expired!")
        return redirect(url_for('login'))


# ----------------------------------- #
#        Login returns jwt token      #
# ----------------------------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = get_user(request.form['username-field'], request.form['password-field'])
            token = generate_token(user[0], user[3])
            session['token'] = token
            return redirect(url_for('profile'))

        except argon2.exceptions.VerifyMismatchError:
            return jsonify({"message": "Invalid username or password"}), 401
    else:
        return render_template("login.html")

# ----------------------------------- #
#  Returns the user object in the DB  #
# ----------------------------------- #

def get_user(username, password):
    cursor = cnx.cursor()

    cursor.execute("select * from User where username = %s", (username,))
    user = cursor.fetchone()
    print(user)

    if argon2.verify_password(bytes(user[2]), password.encode('utf-8')):
        return user

    return None

# ----------------------------------- #
#     Get username from DB using id   #
# ----------------------------------- #

def get_username(user_id):
    cursor = cnx.cursor()

    cursor.execute("SELECT username FROM User WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user is not None:
        return user[0]

    return None

# ----------------------------------- #
#  Returns JWT token from userid      #
# ----------------------------------- #

def generate_token(id, permission):
    payload = {
        "id": id,
        "permission": permission,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token
    
# ----------------------------------- #
#         UPLOAD FILE FOR QUIZ        #
# ----------------------------------- #

@app.route("/upload", methods=['POST'])
def get_uploaded_file():
    try:
        if 'token' not in session:
            return "<h1>User not logged in!</h1>"

        token = session['token']
        json_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        student_id = json_token['id']
        print(student_id)

        if json_token['permission'] != 1:
            return "<h1>Unauthorized access!</h1>"
        
    except jwt.exceptions.ExpiredSignatureError:
        return "<h1>Expired session!</h1>"
        
    uploaded_file = request.files['uploaded-file']

    if 'uploaded-file' not in request.files:
        return render_template('error_uploading.html')

    if len(uploaded_file.filename) == 0:
        return render_template('error_uploading.html')

    app.config['UPLOAD_FOLDER'] = './static/uploads/'

    #! Uncomment when ready
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

    # ! Uncomment when ready
    # insert_quiz(quiz, student_id)

    filename = secure_filename(uploaded_file.filename)
    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], f'quiz-source.{filename.split(".")[-1]}'))
    text = convert_file_to_text(os.path.join(app.config['UPLOAD_FOLDER'], f'quiz-source.{filename.split(".")[-1]}'))

    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'quiz-source.txt'), 'w', encoding="utf-8") as f:
        f.write(text)

    return redirect(url_for('home'))

# ----------------------------------- #
#     Inserts the quiz in the DB      #
# ----------------------------------- #

def write_correct_answers(quiz_id, quiz):
    file_path = os.path.join("Student_answers", "correct_answers", f"{quiz_id}_correct_answers.txt")
    
    with open(file_path, "w") as file:
        for question in quiz:
            file.write(f"{question['right_answer']}\n")

def insert_quiz(quiz, owner_id):
    cursor = cnx.cursor()

    cursor.execute("INSERT INTO quiz (name, ownerId) VALUES (%s, %s)", ('Quiz Name', owner_id))
    quiz_id = cursor.lastrowid

    for i, q in enumerate(quiz):
        cursor.execute("INSERT INTO questions (quiz_id, question_text) VALUES (%s, %s)", (quiz_id, q['question']))
        question_id = cursor.lastrowid

        for j, a in enumerate(q['answers']):
            is_correct = (a[0].upper() == q['right_answer'].upper())
            print("IsCorrect: ", is_correct, "\n Answer: ", a, "\n Right Answer: ", q['right_answer'])
            cursor.execute("INSERT INTO options (question_id, option_text, is_correct) VALUES (%s, %s, %s)", (question_id, a, is_correct))
    write_correct_answers(quiz_id, quiz)
    cnx.commit()
    cursor.close()


# ----------------------------------- #
#  Returns a specific quiz by its id  #
# ----------------------------------- #

def get_quiz(quiz_id):
    cursor = cnx.cursor()

    cursor.execute("SELECT * FROM quiz WHERE id = %s", (quiz_id,))
    quiz_row = cursor.fetchone()

    if quiz_row is None:
        return None

    quiz = []

    cursor.execute("SELECT * FROM questions WHERE quiz_id = %s", (quiz_id,))
    question_rows = cursor.fetchall()

    for question_row in question_rows:
        question = {'question': question_row[2], 'answers': [], 'right_answer': None}

        cursor.execute("SELECT * FROM options WHERE question_id = %s", (question_row[0],))
        option_rows = cursor.fetchall()

        for option_row in option_rows:
            question['answers'].append(option_row[2])
            if option_row[3]:
                question['right_answer'] = option_row[2]

        quiz.append(question)

    cursor.close()
    return quiz


# ----------------------------------- #
#  Gets all the quizzes by the userid #
# ----------------------------------- #

def get_quizzes_by_user(user_id):
    cursor = cnx.cursor()

    cursor.execute("SELECT id, name FROM quiz WHERE ownerId = %s", (user_id,))
    quiz_rows = cursor.fetchall()

    quizzes = []
    for row in quiz_rows:
        quizzes.append({
            'id': row[0],
            'name': row[1]
        })

    cursor.close()
    return quizzes


# ----------------------------------- #
#  Template generator example /quiz/1 #
#       returns the quiz with id 1    #
# ----------------------------------- #

@app.route("/quiz/<int:quiz_id>")
def quiz(quiz_id):
    try:
        if 'token' not in session:
            flash("Either no account detected or session expired!")
    except jwt.exceptions.ExpiredSignatureError:
        flash("Either no account detected or session expired!")
        return redirect(url_for('login'))
    
    quiz = get_quiz(quiz_id)
    if quiz is None:
        return "Quiz not found", 404
    print(quiz)
    return render_template('quiz.html', quiz=quiz, quiz_id=quiz_id, is_logged_in=session.get('token', False))

# --------------------------------------------- #
#    Handles quiz submitting with generating a  #
#    file in this format quizId_studentId.txt   #
# --------------------------------------------- #

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    form_data = request.form
    selected_options = []
    for key, value in form_data.items():
        if key.startswith('question_'):
            if value:
                selected_options.append(value)

    post_request_text = '\n'.join(selected_options)
    try:
        token = session['token']
        json_token_student = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        student_id = json_token_student['id']
        print(student_id)
    except jwt.exceptions.ExpiredSignatureError:
        return "<h1>Expired session!</h1>"
    
    directory = "Student_answers/correct_answers"
    filename = f'{quiz_id}_{student_id}.txt'
    filepath = os.path.join(directory, filename)
    os.makedirs(directory, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(post_request_text)
    return 'Quiz submitted! Answers saved in ' + filename


# --------------------------------------------- #
#  My profile page where quizzes are displayed  #
# --------------------------------------------- #

@app.route('/profile')
def profile():
    try:
        if 'token' not in session:
            flash("Either no account detected or session expired!")
            return redirect(url_for('login'))

        token = session['token']
        json_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        user_id = json_token['id']
        quizzes = get_quizzes_by_user(user_id)

        # ? IF there is time implement different messages

        print(quizzes)

        return render_template('profile.html', quizzes=quizzes, username=get_username(user_id), is_logged_in=session.get('token', False))
    except jwt.exceptions.ExpiredSignatureError:
        flash("Either no account detected or session expired!")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    cnx.close()

# ----------------------------------- #
#  Used if a new database is created  #
# ----------------------------------- #
# def create_quiz_tables():
#     cursor = cnx.cursor()
#     cursor.execute("""
#         CREATE TABLE quiz (
#             id INT AUTO_INCREMENT PRIMARY KEY, 
#             name VARCHAR(255),
#             ownerId BIGINT UNSIGNED NOT NULL,
#             FOREIGN KEY (ownerId) REFERENCES user(id)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE questions (
#             id INT AUTO_INCREMENT PRIMARY KEY, 
#             quiz_id INT NOT NULL, 
#             question_text TEXT, 
#             FOREIGN KEY (quiz_id) REFERENCES quiz(id)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE options (
#             id INT AUTO_INCREMENT PRIMARY KEY, 
#             question_id INT NOT NULL, 
#             option_text TEXT, 
#             is_correct BOOLEAN, 
#             FOREIGN KEY (question_id) REFERENCES questions(id)
#         )
#     """)

#     cursor.close()

# create_quiz_tables()
