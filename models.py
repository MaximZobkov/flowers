import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS flowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_flower(name, description, price, image):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO flowers (name, description, price, image) VALUES (?, ?, ?, ?)',
              (name, description, price, image))
    conn.commit()
    conn.close()

def get_flowers():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM flowers')
    flowers = c.fetchall()
    conn.close()
    return flowers

def get_flower(flower_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM flowers WHERE id = ?', (flower_id,))
    flower = c.fetchone()
    conn.close()
    return flower
