from flask import Flask, render_template, request, redirect, url_for, flash
import os

from werkzeug.utils import secure_filename

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

    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'quiz-source.txt'))


    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)