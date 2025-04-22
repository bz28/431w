from flask import Flask, render_template, request, redirect, url_for 
import sqlite3 as sql
import hashlib
import random
import string

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
                return redirect(url_for('sellerhome')) # Sends user to seller portal if it is a seller
            elif result and role == "Buyers":
                return redirect(url_for('buyerhome')) # Sends user to buyer portal if it is a seller
            elif result and role == "Helpdesk":
                return redirect(url_for('helpdeskhome')) # Sends user to helpdesk portal if it is a seller
            else:
                error = 'Invalid email or password' 
    return render_template('login.html', error=error)

@app.route('/logout') #ijfioagsdngo
def logout():
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/selectrole', methods=['GET', 'POST'])
def selectrole():
    if request.method == 'POST': # redirect user based on role selection
        role = request.form.get('role')  # Make sure your form has `name="role"`
        if role == 'buyer':
            return redirect(url_for('buyerregistration'))
        elif role == 'seller':
            return redirect(url_for('sellerregistration'))
        elif role == 'helpdesk':
            return redirect(url_for('helpdeskregistration'))
    return render_template('select_role.html')

@app.route('/sellerregistration')
def sellerregistration():
    return render_template('seller_registration.html')

@app.route('/buyerregistration', methods=['GET', 'POST'])
def buyerregistration():
    if request.method == 'POST':
        # Get form data
        email = request.form['Email']
        password = request.form['Password']
        business_name = request.form['BusinessName']
        street_name = request.form['StreetName']
        street_num = request.form['StreetNum']
        city = request.form['City']
        state = request.form['State']
        zipcode = request.form['Zipcode']
        
        connection = sql.connect('database.db')
        cursor = connection.cursor()

        buyer_address_id = generate_unique_id(cursor, "Buyers", "buyer_address_id", 32) # Generates a id for address that is not being used
        address_id = buyer_address_id # ensures address and buyer address entries are identical
        
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() # Hash the password

        # Save to database
        cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?)', (email, hashed_password)) # Insert into Users table
        cursor.execute('INSERT INTO Buyers (email, business_name, buyer_address_id) VALUES (?, ?, ?)', (email, business_name, buyer_address_id)) # Insert into Buyers table
        cursor.execute('INSERT INTO Address (address_id, zipcode, street_num, street_name) VALUES (?, ?, ?, ?)', (address_id, zipcode, street_num, street_name)) # Insert into Address table
        cursor.execute('INSERT INTO Zipcode_Info (zipcode, city, state) VALUES (?, ?, ?)', (zipcode, city, state)) # Insert into Zipcode table
        connection.commit()
        connection.close()
        return redirect(url_for('login')) # Redirect to login page after successful registration

    return render_template('buyer_registration.html')

@app.route('/helpdeskregistration')
def helpdeskregistration():
    return render_template('helpdesk_registration.html')

@app.route('/sellerhome')
def sellerhome():
    return render_template('seller_homepage.html')

@app.route('/buyerhome')
def buyerhome():
    return render_template('buyer_homepage.html')

@app.route('/helpdeskhome')
def helpdeskhome():
    return render_template('helpdesk_homepage.html')

def generate_unique_id(cursor, table, column, length):
    while True:
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        cursor.execute(f"SELECT 1 FROM {table} WHERE {column} = ?", (random_id,))
        if not cursor.fetchone():
            return random_id

def check_login(email, password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM Users WHERE email = ? AND password = ?', (email, password)) # Checks if entry is a valid user in the Users table
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
        return "Sellers" # Selects Sellers if user is in Sellers table
    cursor.execute('SELECT COUNT(*) FROM Buyers WHERE email = ?', (email,))
    result = cursor.fetchone()
    if (result[0] == 1):
        connection.close()
        return "Buyers" # Selects Buyers if user is in Buyers table
    cursor.execute('SELECT COUNT(*) FROM Helpdesk WHERE email = ?', (email,))
    result = cursor.fetchone()
    if (result[0] == 1):
        connection.close()
        return "Helpdesk" # Selects Helpdesk if user is in Helpdesk table
    connection.close()
    return "Not Found" # If the user's role cannot be found send error

if __name__ == "__main__":
    app.run(debug=True)