import sqlite3

def get_db_connection():
    conn = sqlite3.connect('residents.db')
    return conn

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def get_all_residents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM residents')
    residents = cursor.fetchall()
    conn.close()
    return residents

def get_resident(apartment_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM residents WHERE apartment_number = ?', (apartment_number,))
    resident = cursor.fetchone()
    conn.close()
    return resident

def add_or_update_resident(apartment_number, resident_type, owner_name, owner_contact, owner_email, resident_name, resident_contact, maintenance_paid, defaulted_amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO residents (apartment_number, resident_type, owner_name, owner_contact, owner_email, resident_name, resident_contact, maintenance_paid, defaulted_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(apartment_number) DO UPDATE SET
        resident_type = excluded.resident_type,
        owner_name = excluded.owner_name,
        owner_contact = excluded.owner_contact,
        owner_email = excluded.owner_email,
        resident_name = excluded.resident_name,
        resident_contact = excluded.resident_contact,
        maintenance_paid = excluded.maintenance_paid,
        defaulted_amount = excluded.defaulted_amount
    ''', (apartment_number, resident_type, owner_name, owner_contact, owner_email, resident_name, resident_contact, maintenance_paid, defaulted_amount))
    conn.commit()
    conn.close()
