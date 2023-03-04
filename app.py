from flask import Flask
from flask import send_file
from flask import render_template
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for
from flask import session
import jinja2
import json
import sqlite3
import os
from os.path import join, dirname, realpath
from db import MySQLDatabase
import config


IMAGES_PATH = join(dirname(realpath(__file__)), 'static/img/')
RESOURCES_PATH = join(dirname(realpath(__file__)), '/var/www/FlaskApp/resources/')

app = Flask(__name__)
env = jinja2.Environment(loader=jinja2.FileSystemLoader(['templates/'])) 
app.secret_key = config.SECRET_KEY

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
    file_path = os.path.join(RESOURCES_PATH, file_name) # utwórz pełną ścieżkę do pliku
    return send_file(file_path, as_attachment=True) # pobierz plik z serwera i zwróć go jako załącznik

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
        user = cnx.execute_query(query,(username,password))
       
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

if __name__ == "__main__":
   app.run()
