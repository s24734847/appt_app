import sqlite3

def setup_database():
    conn = sqlite3.connect('residents.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    ''')

    # Create residents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS residents (
        apartment_number TEXT PRIMARY KEY,
        resident_type TEXT,
        owner_name TEXT,
        owner_contact TEXT,
        owner_email TEXT,
        resident_name TEXT,
        resident_contact TEXT,
        maintenance_paid TEXT,
        defaulted_amount REAL
    )
    ''')

    conn.commit()
    conn.close()

setup_database()

