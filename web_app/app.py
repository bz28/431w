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
                session["seller_email"] = email
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
        role = request.form.get('role') # Make sure your form has `name="role"`
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

    # Build query and parameters
    sql_query = '''
        SELECT * FROM Product_Listings
        WHERE (Product_Name LIKE ? OR Product_Description LIKE ? OR Category LIKE ? OR Seller_Email LIKE ?)
    '''
    params = [f'%{query}%'] * 4 if query else ['%%'] * 4

    if min_price:
        sql_query += " AND CAST(REPLACE(REPLACE(REPLACE(Product_Price, '$', ''), ',', ''), ' ', '') AS REAL) >= ?"
        params.append(float(min_price))
    if max_price:
        sql_query += " AND CAST(REPLACE(REPLACE(REPLACE(Product_Price, '$', ''), ',', ''), ' ', '') AS REAL) <= ?"
        params.append(float(max_price))
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
@app.route('/productreviews', methods=['GET', 'POST'])
def productreviews():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    # Given Listing_ID from Product_Listing
    cursor.execute('SELECT seller_email FROM Product_Listings WHERE listing_id = ?', (session['listing_id'],))
    seller_email = cursor.fetchall()
    session['seller_email'] = seller_email[0][0] # Get Seller Info
    cursor.execute('SELECT business_name FROM Sellers WHERE email = ?', (session['seller_email'],))
    business_name = cursor.fetchall()
    cursor.execute('SELECT AVG(R.Rate) AS Average_Rate FROM Orders O JOIN Reviews R ON O.Order_ID = R.Order_ID WHERE O.Seller_Email = ? GROUP BY O.Seller_Email;', (session['seller_email'],))
    rating = cursor.fetchall()
    cursor.execute('SELECT product_price FROM Product_Listings WHERE listing_id = ?', (session['listing_id'],))
    product_price = cursor.fetchall()
    # Get Product info
    # Get Reviews
    # stores order info ()
    # Order_ID,Seller_Email,Listing_ID,Buyer_Email,Date,Quantity,Payment
    session['business_name'] = business_name
    session['rating'] = rating
    session['product_price'] = product_price
    connection.commit()
    connection.close()
    return render_template('product_reviews.html', business_name=business_name, rating=rating, product_price=product_price)

@app.route('/buy_now', methods=['GET', 'POST'])
def buy_now():
    if 'email' not in session:
        return redirect(url_for('login'))

    buyer_email = session['email']
    listing_id = session['listing_id']
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
        order_id = generate_unique_integer_id(cursor, "Orders", "Order_ID", 3)
        # Insert into Orders table
        cursor.execute('''
            INSERT INTO Orders (Order_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Quantity, Payment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, seller_email, listing_id, buyer_email, order_date, quantity, payment))
        connection.commit()
        connection.close()
    return render_template('buyer_placeorder.html', listing_id=session['listing_id'])


@app.route('/leave_review', methods=['GET', 'POST'])
def leave_review(): #buyers review
    listing_id = request.args.get('listing_id')

    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']
        reviewer_email = session.get('email')  # Assumes you're using session auth

        connection = sql.connect('database.db')
        cursor = connection.cursor()

        # You might want to generate a unique review ID or use autoincrement
        cursor.execute('''
            INSERT INTO Reviews (Listing_ID, Reviewer_Email, Rating, Comment)
            VALUES (?, ?, ?, ?)
        ''', (listing_id, reviewer_email, rating, comment))

        connection.commit()
        connection.close()

        return redirect(url_for('buyerhome'))

    return render_template('leave_review.html', listing_id=listing_id)

@app.route('/sellerreviews', methods=['GET', 'POST'])
def sellerreviews():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT business_name FROM Sellers WHERE email = ?', (session['seller_email'],))
    business_name = cursor.fetchall()
    cursor.execute('SELECT AVG(R.Rate) AS Average_Rate FROM Orders O JOIN Reviews R ON O.Order_ID = R.Order_ID WHERE O.Seller_Email = ? GROUP BY O.Seller_Email;', (session['seller_email'],))
    rating = cursor.fetchall()
    business_name = business_name[0][0]
    rating = rating[0][0]
    connection.commit()
    connection.close()
    return render_template('seller_reviews.html', business_name=business_name, rating=rating)

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
    query = '''
    SELECT 
        p.*,
        IFNULL(AVG(r.rate), 0) as average_rating,
        COUNT(r.order_id) as review_count
    FROM 
        Product_Listings p, 
        Orders o, 
        Reviews r
    WHERE 
        p.listing_id = o.listing_id 
        AND o.order_id = r.order_id
        AND p.seller_email = ?
    GROUP BY 
        p.listing_id
    '''
    
    cursor.execute(query, (email,))
    products_with_reviews = cursor.fetchall()
    
    # Get products without reviews
    query_no_reviews = '''
    SELECT 
        p.*,
        0 as average_rating,
        0 as review_count
    FROM 
        Product_Listings p
    WHERE 
        p.seller_email = ?
        AND p.listing_id NOT IN (
            SELECT DISTINCT o.listing_id 
            FROM Orders o, Reviews r 
            WHERE o.order_id = r.order_id
        )
    '''
    
    cursor.execute(query_no_reviews, (email,))
    products_without_reviews = cursor.fetchall()
    
    # Combine the results
    products = products_with_reviews + products_without_reviews
    
    # Get column names for reference
   
    
    connection.close()
    return render_template('seller_products.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # Initialize variables for template
    show_new_category = False
    form_data = {}
    error = None
    
    if request.method == 'POST':
        # Get the seller's email from the session
        seller_email = session['email']
        
        # Get form data
        product_title = request.form['product_title']
        product_name = request.form['product_name']
        category_selection = request.form['category']
        
        # Handle category selection
        if category_selection == 'new':
            # If user selected "new" but didn't provide a new category name
            if 'new_category' not in request.form or not request.form['new_category'].strip():
                # Save form data to repopulate the form
                form_data = {
                    'product_title': product_title,
                    'product_name': product_name,
                    'category': category_selection,
                    'product_description': request.form.get('product_description', ''),
                    'quantity': request.form.get('quantity', ''),
                    'product_price': "$" +request.form.get('product_price', ''),
                    'status': request.form.get('status', '')
                    
                }
                show_new_category = True
                error = "Please provide a name for the new category"
                return render_template('seller_addproducts.html', 
                                      show_new_category=show_new_category, 
                                      form_data=form_data,
                                      error=error)
            
            category = request.form['new_category']
        else:
            category = category_selection
            
        product_description = request.form['product_description']
        quantity = request.form['quantity']
        product_price = "$" + request.form['product_price']
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
    # Or if we need to show the form again due to validation errors
    return render_template('seller_addproducts.html', 
                          show_new_category=show_new_category, 
                          form_data=form_data,
                          error=error)


@app.route('/seller_orders')
def seller_orders():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    # Only fetch orders that are not shipped or cancelled
    cursor.execute('SELECT * FROM Orders WHERE seller_email = ?', (email,))
    orders = cursor.fetchall()
    
    # Get column names for reference
    cursor.execute('PRAGMA table_info(Orders)')
    columns = [column[1] for column in cursor.fetchall()]
    
    connection.close()
    return render_template('seller_orders.html', orders=orders, columns=columns)

@app.route('/update_order_status/<order_id>', methods=['GET'])
def update_order_status(order_id):
    if 'email' not in session or session['role'] != "Sellers":
        return redirect(url_for('login'))
    
    seller_email = session['email']
    
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    # First, get the payment amount and listing_id from the order
    cursor.execute('SELECT Payment, Listing_ID FROM Orders WHERE Order_ID = ? AND seller_email = ?', 
                  (order_id, seller_email))
    order_info = cursor.fetchone()
    
    if order_info:
        payment, listing_id = order_info
        
        # Update seller's balance by subtracting the payment
        cursor.execute('UPDATE Sellers SET balance = balance - ? WHERE email = ?', 
                      (payment, seller_email))
        
        # Update product quantity and status in Product_Listings
        cursor.execute('''
            UPDATE Product_Listings 
            SET Quantity = Quantity + 1,
                Status = CASE WHEN Status = 2 THEN 1 ELSE Status END
            WHERE Listing_ID = ?
        ''', (listing_id,))
        
        # Finally, delete the order
        cursor.execute('DELETE FROM Orders WHERE Order_ID = ? AND seller_email = ?', 
                      (order_id, seller_email))
        
        connection.commit()
    
    connection.close()
    
    return redirect(url_for('seller_orders'))

@app.route('/order_confirmation', methods = ['GET'])
def order_confirmation():
    return render_template('credit_card.html')

if __name__ == "__main__":
    app.run(debug=True)