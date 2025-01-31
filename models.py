# models.py
import sqlite3


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS flowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            image_paths TEXT,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Добавление товара
def add_flower(name, description, price, image_paths, category):
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO flowers (name, description, price, image_paths, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, price, image_paths, category))
    conn.commit()
    conn.close()


# Получение всех товаров
def get_flowers():
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM flowers ORDER BY name')
    flowers = c.fetchall()
    conn.close()
    return flowers


# Получение товара по ID
def get_flower(flower_id):
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM flowers WHERE id = ?', (flower_id,))
    flower = c.fetchone()
    conn.close()
    return flower


# Получение товаров по категории
def get_flowers_by_category(category):
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM flowers WHERE category = ? ORDER BY name', (category,))
    flowers = c.fetchall()
    conn.close()
    return flowers


# Получение всех товаров, сгруппированных по категориям
def get_flowers_grouped_by_category():
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM flowers')
    categories = c.fetchall()
    grouped_flowers = {}
    for category in categories:
        category_name = category[0]
        c.execute('SELECT * FROM flowers WHERE category = ? ORDER BY name', (category_name,))
        flowers = c.fetchall()
        if flowers:
            grouped_flowers[category_name] = flowers
    conn.close()
    return grouped_flowers


# Получение категорий, в которых есть товары
def get_categories_with_flowers():
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM flowers')
    categories = c.fetchall()
    conn.close()
    return [category[0] for category in categories]
