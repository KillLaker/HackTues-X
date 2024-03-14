from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import mysql.connector
import argon2
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jagdhsflkuaysdfo718349871'

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

    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'quiz-source.txt'))

    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = get_user(request.form['username-field'], request.form['password-field'])

            print(user)

            token = generate_token(user[0])
            return jsonify({'token': jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')}), 200
        except argon2.exceptions.VerifyMismatchError:
            return jsonify({"message": "Invalid username or password"}), 401
    else:
        return render_template("login.html")


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
