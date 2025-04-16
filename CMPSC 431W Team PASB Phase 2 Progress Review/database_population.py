import sqlite3
import csv
import hashlib
import os

db_file = "database.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")

with open("Users.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        email, password = row
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO Users (email, password) VALUES (?, ?)", (email, hashed_password))

with open("Users.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        email, password = row
        cursor.execute("INSERT INTO Users (email, password) VALUES (?, ?)", (email, hashed_password))



conn.commit()
conn.close()
print(f"Database {db_file} created successfully!")
