import sqlite3
import hashlib
from datetime import datetime

DATABASE = 'database1.db'

class User:
    def __init__(self, username, password, email, roles, phone):
        self.username = username
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.email = email
        self.roles = roles
        self.phone = phone

    def save(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO users (username, password, email, roles, phone) VALUES (?, ?, ?, ?, ?)''', (self.username, self.password, self.email, self.roles, self.phone))
        conn.commit()
        conn.close()

    @staticmethod
    def find_by_email(email):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE email = ?''', (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {'id': user[0], 'username': user[1], 'password': user[2], 'email': user[3], 'roles': user[4], 'phone': user[5]}
        return None
    @staticmethod
    def find_by_id(id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE id = ?''', (id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {'id': user[0], 'username': user[1], 'password': user[2], 'email': user[3], 'roles': user[4], 'phone': user[5]}
        return None

    @staticmethod
    def delete(email):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM users WHERE email = ?''', (email,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def user_details_for_email(user_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT u.id, u.username, u.email, u.phone, u.roles, a.user_id, a.account_number, a.balance, a.account_type, a.phone
        FROM users u
        LEFT JOIN accounts a ON u.id = a.user_id
        WHERE u.id = ?
        """, (user_id,))
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def user_details():
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT u.id, u.username, u.email, u.phone, u.roles, a.user_id, a.account_number, a.balance, a.account_type, a.phone
        FROM users u
        LEFT JOIN accounts a ON u.id = a.user_id
        """)
        result = cursor.fetchall()
        conn.close()
        return result
    

    @staticmethod
    def update_password(user_id, new_password):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
        conn.commit()
        conn.close()
    @staticmethod
    def update_password(user_id, new_password):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
        conn.commit()
        conn.close()
class Account:
    def __init__(self, account_number, account_holder, account_type, balance, customer_id, date_of_birth, creation_date, closing_date, phone, created_by):
        self.account_number = account_number
        self.account_holder = account_holder
        self.account_type = account_type
        self.balance = balance
        self.customer_id = created_by
        self.date_of_birth = date_of_birth
        self.creation_date = creation_date
        self.closing_date = closing_date
        self.phone = phone
        self.created_by = customer_id

    @staticmethod
    def get_creator_name(created_by):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (created_by,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def save(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO accounts (account_number, account_holder, account_type, balance, customer_id, date_of_birth, creation_date, deletion_date, phone, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (self.account_number, self.account_holder, self.account_type, self.balance, self.customer_id, self.date_of_birth, self.creation_date, self.closing_date, self.phone, self.created_by))
        conn.commit()
        conn.close()
    @staticmethod
    def find_by_account_numbers(account_number):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Account(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        return None
    @staticmethod
    def find_by_email(email):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE user_id = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Account(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        return None

    def deposit(self, amount, account_number):
        self.balance += amount
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''UPDATE accounts SET balance = ? WHERE account_number = ?''', (self.balance, account_number))
        conn.commit()
        conn.close()

    def withdraw(self, amount, account_number):
        if self.balance >= amount:
            self.balance -= amount
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''UPDATE accounts SET balance = ? WHERE account_number = ?''', (self.balance, account_number))
            conn.commit()
            conn.close()
        else:
            raise ValueError('Insufficient balance')

    @staticmethod
    def numbers(phone):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM accounts WHERE phone = ?''', (phone,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Account(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        return None
    @staticmethod
    def numberss(user_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''SELECT accounts.account_number, accounts.account_holder, 
                            accounts.account_type, accounts.balance, accounts.customer_id, 
                            accounts.date_of_birth, accounts.creation_date, accounts.deletion_date, 
                            accounts.phone, accounts.user_id
                            FROM accounts
                            JOIN users ON accounts.customer_id = users.id
                            WHERE accounts.user_id = ?''', (user_id,))

        row = cursor.fetchone()
        conn.close()
        if row:
            return Account(*row)
        return None

    @staticmethod
    def number(user_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''SELECT accounts.account_number, accounts.account_holder, 
                            accounts.account_type, accounts.balance, accounts.customer_id, 
                            accounts.date_of_birth, accounts.creation_date, accounts.deletion_date, 
                            accounts.phone, accounts.user_id, users.username AS creator_name
                            FROM accounts
                            JOIN users ON accounts.customer_id = users.id
                            WHERE accounts.user_id = ?''', (user_id,))

        row = cursor.fetchone()
        conn.close()
        if row:
            account_data = row[:-1] 
            account = Account(*account_data)
            creator_name = row[-1]  
            return account, creator_name
        return None, None



    @staticmethod
    def delete(account_number):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM accounts WHERE account_number = ?''', (account_number,))
        conn.commit()
        conn.close()

import sqlite3
from datetime import datetime

class Transaction:
    def __init__(self, account_number, transaction_type, amount, receiver_account_number):
        self.account_number = account_number
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.receiver_account_number = receiver_account_number

    def save(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO transactions (account_number, transaction_type, amount, date, receiver_account_number) VALUES (?, ?, ?, ?, ?)''', 
                       (self.account_number, self.transaction_type, self.amount, self.timestamp, self.receiver_account_number))
        conn.commit()
        conn.close()

    @staticmethod
    def find_by_account_number(account_number):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM transactions WHERE account_number = ? ORDER BY date DESC''', (account_number,))
        transactions = cursor.fetchall()
        conn.close()
        return [{'account_number': t[1], 'transaction_type': t[2], 'amount': t[3], 'timestamp': t[4], 'receiver_account_number': t[5]} for t in transactions]

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, email TEXT UNIQUE, roles TEXT, phone TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_number TEXT PRIMARY KEY, account_holder TEXT, account_type TEXT, balance REAL, customer_id INTEGER, date_of_birth TEXT, creation_date TEXT, closing_date TEXT, phone TEXT, created_by INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, account_number TEXT, transaction_type TEXT, amount REAL, timestamp TEXT)''')
    conn.commit()
    conn.close()
