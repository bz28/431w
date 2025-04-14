import sqlite3
import csv
import hashlib
import os
print("Current working directory:", os.getcwd())
print("Files in directory:", os.listdir())


csv_file = "Users.csv"
db_file = "database.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS Users (email TEXT, password TEXT, PRIMARY KEY (email))")

with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        email, password = row
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO Users (email, password) VALUES (?, ?)", (email, hashed_password))
conn.commit()
conn.close()

print(f"Database {db_file} created successfully!")
