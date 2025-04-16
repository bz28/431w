from flask import Flask, render_template, request, redirect, url_for 
import sqlite3 as sql
import hashlib

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

@app.route('/')
def index():
    return render_template('User Login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    result = None
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() 
        if email and hashed_password: 
            result = check_login(email, hashed_password) 
            if result:
                return redirect(url_for('home')) 
            else:
                error = 'Invalid email or password' 
    return render_template('User Login.html', error=error)

@app.route('/home')
def home():
    return render_template('Buyer Home.html')

def check_login(email, password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM Users WHERE email = ? AND password = ?', (email, password))
    result = cursor.fetchone()
    connection.close()
    return result[0] == 1

if __name__ == "__main__":
    app.run(debug=True)


