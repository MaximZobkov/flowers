# models.py
import json
import sqlite3

# Path to the promo codes file
PROMO_CODES_FILE = 'promo_codes.json'


def load_promo_codes():
    with open(PROMO_CODES_FILE, 'r') as file:
        return json.load(file)


def save_promo_codes(promo_codes):
    with open(PROMO_CODES_FILE, 'w') as file:
        json.dump(promo_codes, file, indent=4)


def get_promo_code(code):
    promo_codes = load_promo_codes()
    return promo_codes['promo_codes'].get(code)


def use_promo_code(code):
    promo_codes = load_promo_codes()
    if code in promo_codes['promo_codes'] and promo_codes['promo_codes'][code]['uses_left'] > 0:
        promo_codes['promo_codes'][code]['uses_left'] -= 1
        save_promo_codes(promo_codes)
        return True
    return False


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


def get_path(flower_id):
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('SELECT image_paths FROM flowers WHERE id = ?', (flower_id,))
    path = c.fetchone()
    conn.close()
    return path


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


# Обновление товара
def update_flower(flower_id, name, description, price, image_paths, category):
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('''
        UPDATE flowers
        SET name = ?, description = ?, price = ?, image_paths = ?, category = ?
        WHERE id = ?
    ''', (name, description, price, image_paths, category, flower_id))
    conn.commit()
    conn.close()


# Удаление товара
def delete_flower(flower_id):
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('DELETE FROM flowers WHERE id = ?', (flower_id,))
    conn.commit()
    conn.close()
