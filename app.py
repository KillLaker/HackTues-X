from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import mysql.connector
import argon2
import jwt
import datetime
import CreateStatistics
from flask import Flask, render_template, request, redirect, url_for, flash
from jinja2 import Environment, PackageLoader, select_autoescape
from openaiApi import generate_multiple_choice_questions
from openai import OpenAI
from werkzeug.utils import secure_filename
from convert_files_to_txt import *
from dotenv import load_dotenv
from student_answers import combine_student_answers
from flask import url_for

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

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html', is_logged_in=session.get('token', False))

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

        except (argon2.exceptions.VerifyMismatchError, TypeError):
            return redirect(url_for('login', trigger_alert = True))
    else:
        trigger_alert = request.args.get('trigger_alert', type=bool)

        return render_template("login.html", trigger_alert = trigger_alert)


@app.route('/logout', methods = ['GET'])
def logout():
    try:
        if 'token' not in session:
            flash("Either no account detected or session expired!")
            return redirect(url_for('login', trigger_alert = True))

        session.pop('token', None)
    except jwt.exceptions.ExpiredSignatureError:
        return redirect(url_for('login', trigger_alert=True))

    return redirect(url_for('login'))

# ----------------------------------- #
#  Returns the user object in the DB  #
# ----------------------------------- #

def get_user(username, password):
    cursor = cnx.cursor()

    cursor.execute("select * from User where username = %s", (username,))
    user = cursor.fetchone()
    # print(user)

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
        # print(student_id)

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

    filename = secure_filename(uploaded_file.filename)
    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], f'quiz-source.{filename.split(".")[-1]}'))
    text = convert_file_to_text(os.path.join(app.config['UPLOAD_FOLDER'], f'quiz-source.{filename.split(".")[-1]}'))

    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'quiz-source.txt'), 'w', encoding="utf-8") as f:
        f.write(text)

    quiz = generate_multiple_choice_questions()
    insert_quiz(quiz, student_id)

    return redirect(url_for('profile'))

# ----------------------------------- #
#     Inserts the quiz in the DB      #
# ----------------------------------- #

def write_correct_answers(quiz_id, quiz):
    file_path = os.path.join("Student_answers", "correct_answers", f"{quiz_id}_correct_answers.txt")
    
    with open(file_path, "w") as file:
        for question in quiz:
            file.write(f"{question['right_answer']}\n")
        
def get_prev_quiz_id():
    cursor = cnx.cursor()
    cursor.execute("SELECT id FROM quiz ORDER BY id DESC LIMIT 1")
    quiz_id = cursor.fetchone()
    cursor.close()
    if quiz_id:
        return quiz_id[0]
    else:
        return None

def insert_quiz(quiz, owner_id):
    cursor = cnx.cursor()

    name = "Quiz 1"

    prevQuizId = get_prev_quiz_id()
    if prevQuizId is not None:
        name = "Quiz " + str(get_prev_quiz_id() + 1)

    cursor.execute("INSERT INTO quiz (name, ownerId) VALUES (%s, %s)", (name, owner_id))
    quiz_id = cursor.lastrowid

    for i, q in enumerate(quiz):
        cursor.execute("INSERT INTO questions (quiz_id, question_text) VALUES (%s, %s)", (quiz_id, q['question']))
        question_id = cursor.lastrowid

        for j, a in enumerate(q['answers']):
            is_correct = (a[0].upper() == q['right_answer'].upper())
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

    quiz_name = quiz_row[1]
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
    return quiz_name, quiz


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
            return redirect(url_for('login', trigger_alert = True))
    except jwt.exceptions.ExpiredSignatureError:
        flash("Either no account detected or session expired!")
        return redirect(url_for('login', trigger_alert = True))
    
    quiz_name, quiz = get_quiz(quiz_id)
    if quiz is None:
        return "Quiz not found", 404
    return render_template('quiz.html', quiz_name=quiz_name,  quiz=quiz, quiz_id=quiz_id, is_logged_in=session.get('token', False))

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
        # print(student_id)
    except jwt.exceptions.ExpiredSignatureError:
        return "<h1>Expired session!</h1>"
    
    directory = "Student_answers/"
    filename = f'{quiz_id}_{student_id}.txt'
    filepath = os.path.join(directory, filename)
    os.makedirs(directory, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(post_request_text)
    combine_student_answers(directory)

    quiz_name, quiz = get_quiz(quiz_id)
    if quiz is None:
        return "Quiz not found", 404
    
    correct_answers_full = [q['right_answer'] for q in quiz]
    correct_answers = [answer[0].upper() for answer in correct_answers_full]
    num_correct = sum(a == b for a, b in zip(selected_options, correct_answers))

    return render_template('results.html', quiz=quiz, num_correct=num_correct, total_questions=len(selected_options), selected_options=selected_options, correct_options=correct_answers, is_logged_in=session.get('token', False))

# --------------------------------------------- #
#  My profile page where quizzes are displayed  #
# --------------------------------------------- #

@app.route('/profile')
def profile():
    try:
        if 'token' not in session:
            flash("Either no account detected or session expired!")
            return redirect(url_for('login', trigger_alert = True))

        token = session['token']
        json_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        user_id = json_token['id']
        quizzes = get_quizzes_by_user(user_id)

        return render_template('profile.html', quizzes=quizzes, username=get_username(user_id), is_logged_in=session.get('token', False), teacher=json_token['permission'] == 1)
    except jwt.exceptions.ExpiredSignatureError:
        return redirect(url_for('login', trigger_alert = True))

@app.route('/quiz/<int:quiz_id>/statistics')
def get_statistics(quiz_id):
    try:
        if 'token' not in session:
            flash("Either no account detected or session expired!")
    except jwt.exceptions.ExpiredSignatureError:
        flash("Either no account detected or session expired!")
        return redirect(url_for('login'))

    diagrams_files = [url_for('static', filename=f"Diagrams/{file}") for file in os.listdir('static/Diagrams') if file.endswith('.png')]
    statistics_files = [url_for('static', filename=f"Statistics/{file}") for file in os.listdir('static/Statistics') if file.endswith('.png')]
    
    CreateStatistics.create_statistics(quiz_id)

    quiz_name, quiz = get_quiz(quiz_id)
    print(quiz[1])

    return render_template('diagrams.html', diagrams_files=diagrams_files, statistics_files=statistics_files, quiz=quiz)


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
