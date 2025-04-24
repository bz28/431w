from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3 as sql
import hashlib
import random
import string
from datetime import datetime

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

app.secret_key = '123456789'

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
                session['email'] = email
                session['role'] = role
                return redirect(url_for('sellerhome')) # Sends user to seller portal if it is a seller
            elif result and role == "Buyers":
                session['email'] = email
                session['role'] = role
                return redirect(url_for('buyerhome')) # Sends user to buyer portal if it is a seller
            elif result and role == "Helpdesk":
                session['email'] = email
                session['role'] = role
                return redirect(url_for('helpdeskhome')) # Sends user to helpdesk portal if it is a seller
            else:
                error = 'Invalid email or password' 
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    if 'email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        email = session['email']
        new_password = request.form['NewPassword']
        hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest() # Hash the new password
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE Users SET password = ? WHERE email = ?', (hashed_password, email)) # Update the password in the database
        connection.commit()
        connection.close()
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', email=session['email'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', email=session['email'], role=session['role'])

@app.route('/selectrole', methods=['GET', 'POST'])
def selectrole():
    if request.method == 'POST': # Redirect user based on role selection
        role = request.form.get('role')  # Make sure your form has `name="role"`
        if role == 'buyer':
            return redirect(url_for('buyerregistration'))
        elif role == 'seller':
            return redirect(url_for('sellerregistration'))
        elif role == 'helpdesk':
            return redirect(url_for('helpdeskregistration'))
    return render_template('select_role.html')

@app.route('/sellerregistration', methods=['GET', 'POST'])
def sellerregistration():
    if request.method == 'POST':
        # Get form data
        email = request.form['Email']
        password = request.form['Password']
        street_name = request.form['StreetName']
        street_num = request.form['StreetNum']
        city = request.form['City']
        state = request.form['State']
        zipcode = request.form['Zipcode']
        business_name = request.form['BusinessName']
        bank_routing_number = request.form['BankRoutingNumber']
        bank_account_number = request.form['BankAccountNumber']
        balance = request.form['Balance']
        # Connect to database
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        business_address_id = generate_unique_id(cursor, "Sellers", "business_address_id", 32) # Generates a id for address that is not being used
        address_id = business_address_id # ensures address and seller address entries are identical
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() # Hash the password
        # Save to database
        cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?)', (email, hashed_password)) # Insert into Users table
        cursor.execute('INSERT INTO Sellers (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance) VALUES (?, ?, ?, ?, ?, ?)', (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance)) # Insert into Sellers table
        cursor.execute('INSERT INTO Address (address_id, zipcode, street_num, street_name) VALUES (?, ?, ?, ?)', (address_id, zipcode, street_num, street_name)) # Insert into Address table
        cursor.execute('INSERT INTO Zipcode_Info (zipcode, city, state) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM Zipcode_Info WHERE zipcode = ?)', (zipcode, city, state, zipcode)) # Insert into Zipcode table
        connection.commit()
        connection.close()
        return redirect(url_for('login')) # Redirect to login page after successful registration
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
        # Connect to database
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        buyer_address_id = generate_unique_id(cursor, "Buyers", "buyer_address_id", 32) # Generates a id for address that is not being used
        address_id = buyer_address_id # ensures address and buyer address entries are identical
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() # Hash the password
        # Save to database
        cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?)', (email, hashed_password)) # Insert into Users table
        cursor.execute('INSERT INTO Buyers (email, business_name, buyer_address_id) VALUES (?, ?, ?)', (email, business_name, buyer_address_id)) # Insert into Buyers table
        cursor.execute('INSERT INTO Address (address_id, zipcode, street_num, street_name) VALUES (?, ?, ?, ?)', (address_id, zipcode, street_num, street_name)) # Insert into Address table
        cursor.execute('INSERT INTO Zipcode_Info (zipcode, city, state) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM Zipcode_Info WHERE zipcode = ?)', (zipcode, city, state, zipcode)) # Insert into Zipcode table
        connection.commit()
        connection.close()
        return redirect(url_for('login')) # Redirect to login page after successful registration

    return render_template('buyer_registration.html')

@app.route('/helpdeskregistration')
def helpdeskregistration():
    return render_template('helpdesk_registration.html')

@app.route('/sellerhome', methods=['GET', 'POST'])
def sellerhome():
    return render_template('seller_homepage.html')


@app.route('/buyerhome', methods=['GET', 'POST'])
def buyerhome():
    query = request.args.get('query', '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    # Get categories
    cursor.execute("SELECT category_name FROM Categories WHERE parent_category = 'Root'")
    root_categories = cursor.fetchall()
    cursor.execute("SELECT C2.category_name FROM Categories C, Categories C2 WHERE C.parent_category = 'Root' and C.category_name = C2.parent_category")
    subcategories = cursor.fetchall()
    cursor.execute("SELECT C3.category_name FROM Categories C1, Categories C2, Categories C3 WHERE C1.parent_category = 'Root' AND C1.category_name = C2.parent_category AND C2.category_name = C3.parent_category GROUP BY C3.parent_category")
    itemscategory = cursor.fetchall()

    # Base query
    sql_query = '''
        SELECT * FROM Product_Listings
        WHERE (Product_Name LIKE ? OR Product_Description LIKE ? OR Category LIKE ? OR Seller_Email LIKE ?)
    '''
    params = [f'%{query}%'] * 4 if query else ['%%'] * 4

    # Cast text price to REAL after removing '$'
    if min_price:
        sql_query += " AND CAST(REPLACE(Product_Price, '$', '') AS REAL) >= ?"
        params.append(min_price)
    if max_price:
        sql_query += " AND CAST(REPLACE(Product_Price, '$', '') AS REAL) <= ?"
        params.append(max_price)

    cursor.execute(sql_query, params)
    products = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    connection.close()
    
    if request.method == 'POST': # Redirect user based on role selection
        session['listing_id'] = request.form.get('listing_id')
        return redirect(url_for('productreviews'))

    return render_template(
        'buyer_homepage.html',
        root_categories=root_categories,
        subcategories=subcategories,
        itemscategory=itemscategory,
        products=products,
        columns=columns
    )

@app.route('/buy_now', methods=['GET', 'POST'])
def buy_now():
    if 'email' not in session:
        return redirect(url_for('login'))

    buyer_email = session['email']
    listing_id = request.form['listing_id']
    order_date = datetime.now().strftime('%Y/%m/%d')

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    # Get product info
    cursor.execute("SELECT seller_email, product_price FROM Product_Listings WHERE listing_id = ?", (listing_id,))
    result = cursor.fetchone()

    if result:
        seller_email, product_price = result
        quantity = 1  # Fixed quantity
        payment = int(product_price.replace('$', '')) * quantity

        # Generate unique order_id
        order_id = generate_unique_integer_id(cursor, "Orders", "Order_ID", 6)

        # Insert into Orders table
        cursor.execute('''
            INSERT INTO Orders (Order_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Quantity, Payment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, seller_email, listing_id, buyer_email, order_date, quantity, payment))

        connection.commit()

    connection.close()
    return render_template('buyer_placeorder.html', listing_id=session['listing_id'])

@app.route('/sellerreviews', methods=['GET', 'POST'])
def sellerreviews():
    return render_template('seller_reviews.html')

@app.route('/productreviews', methods=['GET', 'POST'])
def productreviews():
    return render_template('product_reviews.html')

@app.route('/orders')
def view_orders():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Orders WHERE Buyer_Email = ?', (user_email,))
    orders = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    connection.close()

    order_list = [dict(zip(columns, order)) for order in orders]

    return render_template('buyer_orders.html', orders=order_list)

@app.route('/helpdeskhome')
def helpdeskhome():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("")
    return render_template('helpdesk_homepage.html')

@app.route("/requests")
def requests():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    email = session['email']
    cursor.execute("SELECT request_id, sender_email, request_type, request_desc FROM Requests WHERE helpdesk_staff_email = ?", (email,))
    requests = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    connection.close()
    return render_template("requests.html", requests=requests, columns=columns)


def generate_unique_id(cursor, table, column, length):
    while True:
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        cursor.execute(f"SELECT 1 FROM {table} WHERE {column} = ?", (random_id,))
        if not cursor.fetchone():
            return random_id

def generate_unique_integer_id(cursor, table, column, length):
    while True:
        random_id = ''.join(random.choices(string.digits, k=length))
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





@app.route('/seller_products')
def seller_products():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    # Assuming your table is called Product_listings
    cursor.execute('SELECT * FROM Product_Listings WHERE seller_email = ?', (email,))
    products = cursor.fetchall()
    
    # Get column names for reference
    cursor.execute('PRAGMA table_info(Product_listings)')
    columns = [column[1] for column in cursor.fetchall()]
    
    connection.close()
    return render_template('seller_products.html', products=products, columns=columns)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get the seller's email from the session
        seller_email = session['email']
        
        # Get form data
        product_title = request.form['product_title']
        product_name = request.form['product_name']
        
        # Handle category (check if it's a new category)
        if request.form['category'] == 'new':
            category = request.form['new_category']
        else:
            category = request.form['category']
            
        product_description = request.form['product_description']
        quantity = request.form['quantity']
        product_price = request.form['product_price']
        status = request.form['status']
        
        # Connect to database
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        
        # Generate a unique listing ID
        listing_id = generate_unique_id(cursor, "Product_listings", "Listing_ID", 10)
        
        # Insert into Product_listings table
        cursor.execute('''
            INSERT INTO Product_listings (
                Listing_ID, Seller_Email, Category, Product_Title, 
                Product_Name, Product_Description, Quantity, Product_Price, Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            listing_id, seller_email, category, product_title,
            product_name, product_description, quantity, product_price, status
        ))
        
        connection.commit()
        connection.close()
        
        # Redirect to the seller products page
        return redirect(url_for('seller_products'))
    
    # If it's a GET request, just render the form
    return render_template('seller_addproducts.html')


@app.route('/seller_orders')
def seller_orders():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    # Assuming your table is called Product_listings
    cursor.execute('SELECT * FROM Orders WHERE seller_email = ?', (email,))
    orders = cursor.fetchall()
    
    # Get column names for reference
    cursor.execute('PRAGMA table_info(Orders)')
    columns = [column[1] for column in cursor.fetchall()]
    
    connection.close()
    return render_template('seller_orders.html', orders=orders, columns=columns)

if __name__ == "__main__":
    app.run(debug=True)