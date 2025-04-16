import sqlite3
import csv
import hashlib
import os

#print(os.getcwd())
#os.chdir()

db_file = "database.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Helpdesk (email TEXT, position TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Buyers (email TEXT, business_name TEXT, buyer_address_id TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Sellers (email TEXT, business_name TEXT, business_address_id TEXT, bank_routing_number TEXT, bank_account_number INTEGER, balance INTEGER, PRIMARY KEY (email))")

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

conn.commit()
conn.close()
print(f"Database {db_file} created successfully!")
