from flask import Flask, render_template, request, redirect, url_for 
import sqlite3 as sql
import hashlib

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

@app.route('/')
def index():
    return render_template('login.html')

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
            role = check_role(email)
            if result and role == "Sellers":
                return redirect(url_for('sellerhome')) 
            elif result and role == "Buyers":
                return redirect(url_for('buyerhome')) 
            elif result and role == "Helpdesk":
                return redirect(url_for('helpdeskhome')) 
            else:
                error = 'Invalid email or password' 
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/sellerhome')
def sellerhome():
    return render_template('seller_homepage.html')

@app.route('/buyerhome')
def buyerhome():
    return render_template('buyer_homepage.html')

@app.route('/helpdeskhome')
def helpdeskhome():
    return render_template('helpdesk_homepage.html')

def check_login(email, password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM Users WHERE email = ? AND password = ?', (email, password))
    result = cursor.fetchone()
    connection.close()
    return result[0] == 1

def check_role(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM Sellers WHERE email = ?', (email,))
    result = cursor.fetchone()
    if (result[0] == 1):
        connection.close()
        return "Sellers"
    
    cursor.execute('SELECT COUNT(*) FROM Buyers WHERE email = ?', (email,))
    result = cursor.fetchone()
    if (result[0] == 1):
        connection.close()
        return "Buyers"
    
    cursor.execute('SELECT COUNT(*) FROM Helpdesk WHERE email = ?', (email,))
    result = cursor.fetchone()
    if (result[0] == 1):
        connection.close()
        return "Helpdesk"
    
    connection.close()
    return "Not Found"

if __name__ == "__main__":
    app.run(debug=True)


