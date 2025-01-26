import logging
import os

import requests
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename

import models

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на свой секретный ключ
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Настройки Telegram
TELEGRAM_TOKEN = '7436726184:AAEpRkFBNMfT63moNvD7MCRbXZ9a2rvq6lo'  # Замените на ваш токен API
TELEGRAM_USERNAME = '754086992'  # Замените на имя пользователя, например, @myflowerbot
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Новые категории товаров
CATEGORIES = [
    "Букеты, композиции, корзины",
    "Комнатные растения, грунт, удобрения, кашпо, вазы",
    "Шары и товары для праздника",
    "Мягкие игрушки",
    "Аксессуары, очки, бижутерия",
    "Сувениры",
    "Премиум уходовая косметика",
    "Подарочные пакеты, открытки",
    "Флористическое оформление",
    "Цветы оптом"
]

def crop_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        width, height = img.size
        if width != height:
            if height > width:
                top = (height - width) / 2
                bottom = (height + width) / 2
                left = 0
                right = width
            else:
                left = (width - height) / 2
                right = (width + height) / 2
                top = 0
                bottom = height
            img = img.crop((left, top, right, bottom))
        img.save(image_path)

@app.route('/')
def index():
    category = request.args.get('category')
    categories_with_flowers = models.get_categories_with_flowers()
    if category:
        flowers = models.get_flowers_by_category(category)
        grouped_flowers = {category: flowers}
    else:
        grouped_flowers = models.get_flowers_grouped_by_category()
    return render_template('index.html', grouped_flowers=grouped_flowers, categories=categories_with_flowers)

@app.route('/flower/<int:flower_id>')
def flower(flower_id):
    flower = models.get_flower(flower_id)
    return render_template('product.html', flower=flower)

@app.route('/add', methods=['GET', 'POST'])
def add_flower():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        image_files = request.files.getlist('image')
        image_paths = []
        for image in image_files:
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                crop_image(image_path)  # Обрезка изображения до соотношения 1:1
                image_paths.append(image_path)
        image_paths_str = ','.join(image_paths)
        models.add_flower(name, description, price, image_paths_str, category)
        return redirect(url_for('index'))
    return render_template('add.html', categories=CATEGORIES)

@app.route('/add_to_cart/<int:flower_id>')
def add_to_cart(flower_id):
    flower = models.get_flower(flower_id)
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(flower)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', []))

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/submit_order', methods=['POST'])
def submit_order():
    name = request.form['name']
    phone = request.form['phone']
    cart = session.get('cart', [])
    cart_items = [f"{item[1]} - {item[3]} руб." for item in cart]
    cart_items_str = "\n".join(cart_items)

    message = f"Новый заказ:\n\nИмя: {name}\nТелефон: {phone}\n\nТовары:\n{cart_items_str}"

    # Отправка сообщения через requests
    payload = {
        'chat_id': TELEGRAM_USERNAME,
        'text': message
    }
    response = requests.post(TELEGRAM_API_URL, data=payload)

    # Логирование ответа
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response text: {response.text}")

    if response.status_code == 200:
        return jsonify(success=True)
    else:
        return jsonify(success=False, error=response.text), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    models.init_db()
    app.run(debug=True)
