from flask import Flask
from flask import send_file
from flask import render_template
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for
from flask import session
import jinja2
from jinja2.filters import escape
import json
import os
from os.path import join, dirname, realpath
from db import MySQLDatabase
import config

def get_questions():
    cnx = MySQLDatabase.getInstance()
    query = ("SELECT * FROM `pytania`")
    questions = cnx.execute_query_questions(query)
    return questions

def format_questions(data):
    questions = []

    for row in data:
        question = {}
        question["question"] = row[1]
        question["choices"] = json.loads(row[2])
        question["answer"] = row[3]
        questions.append(question)

    return questions

IMAGES_PATH = join(dirname(realpath(__file__)), 'static/img/')
RESOURCES_PATH = join(dirname(realpath(__file__)), '/var/www/FlaskApp/resources/')

app = Flask(__name__)
env = jinja2.Environment(loader=jinja2.FileSystemLoader(['templates/'])) 
app.secret_key = config.SECRET_KEY
questions = get_questions()
questions = format_questions(questions)

@app.route("/quiz")
def index_quiz():
    return render_template("index_quiz.html", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    score = 0
    for question in questions:
        answer = request.form.get(question["question"])
        if answer == question["answer"]:
            score += 1
    return render_template("result.html", score=score, total=len(questions))

@app.route("/add", methods=["GET", "POST"])
def add():
    if 'logged_in' in session:
        if request.method == "POST":
            question = request.form.get("question")
            choices = request.form.get("choices").split(",")
            choices = json.dumps(choices)
            answer = request.form.get("answer")
            cnx = MySQLDatabase.getInstance()
            query = "INSERT INTO pytania (question, choices, answer) VALUES (%s, %s, %s)"
            val = [question, choices, answer]
            cnx.execute_query_add_question(query, val)
            return render_template("add_question.html", success=True)
        
        else:
            return render_template("add_question.html", success=False)
    else:
        return redirect(url_for('login'))

@app.route('/')
def index():
    try:
        file_list = os.listdir(IMAGES_PATH)
        prace = []
        for file_name in file_list:
            file_path = os.path.join('static/img/', file_name) # utwórz pełną ścieżkę do pliku
            prace.append(file_name)
        return render_template('start.html', prace=prace)
    except:
        return render_template('start.html')

@app.route('/files')
def list_files():
    if 'logged_in' in session:
        file_list = os.listdir(RESOURCES_PATH) # podaj ścieżkę do katalogu, którego zawartość chcesz wyświetlić
        file_links = []
        for file_name in file_list:
            file_path = os.path.join(RESOURCES_PATH, file_name) # utwórz pełną ścieżkę do pliku
            file_links.append(file_name) # utwórz link do pobrania pliku
            #res = ''.join(file_links)
        return render_template('resources.html', links = file_links)
    else:
        return redirect(url_for('login'))

@app.route('/download/<path:file_name>')
def download_file(file_name):
    if 'logged_in' in session:
        file_path = os.path.join(RESOURCES_PATH, file_name) # utwórz pełną ścieżkę do pliku
        return send_file(file_path, as_attachment=True) # pobierz plik z serwera i zwróć go jako załącznik
    else:
        return redirect(url_for('login'))
    
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'logged_in' in session:
        if request.method == 'POST':
            file = request.files['file']
            if file:
                filename = file.filename
                file_path = os.path.join(RESOURCES_PATH, filename) # podaj ścieżkę do katalogu, w którym chcesz zapisać plik
                file.save(file_path)
                return redirect('/')
        else:
            return render_template('upload.html')
    else:
        return redirect(url_for('login'))

@app.route('/kontakt')
def kontakt():
   return render_template('kontakt.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cnx = MySQLDatabase.getInstance()
        query = ("SELECT * FROM users WHERE username = %s AND password = %s")
        user = cnx.execute_query_one(query,(username,password))
       
        if user is not None:
            session['logged_in'] = True
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            error = 'Nieprawidłowa nazwa użytkownika lub hasło.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.context_processor
def inject_variables():
    return dict(
        app_name=config.APP_NAME
        )

if __name__ == "__main__":
  app.run()
