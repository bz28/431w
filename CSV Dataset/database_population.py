import sqlite3
import csv
import hashlib
import os

print(os.getcwd())
#print(os.listdir())
os.chdir("CSV Dataset")
print(os.getcwd())

db_file = "database.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Helpdesk (email TEXT, position TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Buyers (email TEXT, business_name TEXT, buyer_address_id TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Sellers (email TEXT, business_name TEXT, business_address_id TEXT, bank_routing_number TEXT, bank_account_number INTEGER, balance INTEGER, PRIMARY KEY (email))")

cursor.execute("CREATE TABLE IF NOT EXISTS Address (address_id TEXT, zipcode INTEGER, street_num INTEGER, street_name TEXT, PRIMARY KEY (address_id))")
cursor.execute("CREATE TABLE IF NOT EXISTS Credit_Cards (credit_card_num TEXT, card_type TEXT, expire_month INTEGER, expire_year INTEGER, security_code INTEGER, owner_email TEXT, PRIMARY KEY (credit_card_num))")
cursor.execute("CREATE TABLE IF NOT EXISTS Zipcode_Info (zipcode INTEGER, city TEXT, state TEXT, PRIMARY KEY (zipcode))")

cursor.execute("CREATE TABLE IF NOT EXISTS Product_Listings (seller_email TEXT, listing_id INTEGER, category  TEXT, product_title TEXT, product_name TEXT, product_description TEXT, quantity INTEGER, product_price TEXT, status INTEGER, PRIMARY KEY (seller_email, listing_id))")
cursor.execute("CREATE TABLE IF NOT EXISTS Orders (order_id INTEGER, seller_email TEXT, listing_id INTEGER, buyer_email TEXT, date TEXT, quantity INTEGER, payment INTEGER, PRIMARY KEY (order_id))")
cursor.execute("CREATE TABLE IF NOT EXISTS Categories (parent_category TEXT, category_name TEXT, PRIMARY KEY (parent_category))")

cursor.execute("CREATE TABLE IF NOT EXISTS Requests (request_id INTEGER, sender_email TEXT, helpdesk_staff_email TEXT, request_type TEXT, request_desc TEXT, request_status INTEGER, PRIMARY KEY (request_id))")
cursor.execute("CREATE TABLE IF NOT EXISTS Reviews (order_id INTEGER, rate INTEGER, review_desc TEXT, PRIMARY KEY (order_id))")

with open("Users.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        email, password = row
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO Users (email, password) VALUES (?, ?)", (email, hashed_password))
with open("Helpdesk.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        email, position = row
        cursor.execute("INSERT INTO Helpdesk (email, position) VALUES (?, ?)", (email, position))
with open("Buyers.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        email, business_name, buyer_address_id = row
        cursor.execute("INSERT INTO Buyers (email, business_name, buyer_address_id) VALUES (?, ?, ?)", (email, business_name, buyer_address_id))
with open("Sellers.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        email, business_name, business_address_id, bank_routing_number, bank_account_number, balance = row
        cursor.execute("INSERT INTO Sellers (email, business_name, business_address_id, bank_routing_number, bank_account_number,balance) VALUES (?, ?, ?, ?, ?, ?)", (email, business_name, business_address_id, bank_routing_number, bank_account_number,balance))

with open("Address.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        address_id, zipcode, street_num, street_name = row
        cursor.execute("INSERT INTO Address (address_id, zipcode, street_num, street_name) VALUES (?, ?, ?, ?)", (address_id, zipcode, street_num, street_name))
with open("Credit_Cards.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        credit_card_num, card_type, expire_month, expire_year, security_code, owner_email = row
        cursor.execute("INSERT INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email) VALUES (?, ?, ?, ?, ?, ?)", (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email))
with open("Zipcode_Info.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        zipcode, city, state = row
        cursor.execute("INSERT INTO Zipcode_Info (zipcode, city, state) VALUES (?, ?, ?)", (zipcode, city, state))

conn.commit()
conn.close()
print(f"Database {db_file} created successfully!")
